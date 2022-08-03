/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import java.time.Duration;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresUtils.class);

  private static final String PGOUTPUT_PLUGIN = "pgoutput";

  public static final Duration MAX_FIRST_RECORD_WAIT_TIME = Duration.ofMinutes(20);
  public static final Duration DEFAULT_FIRST_RECORD_WAIT_TIME = Duration.ofMinutes(5);

  public static String getPluginValue(final JsonNode field) {
    return field.has("plugin") ? field.get("plugin").asText() : PGOUTPUT_PLUGIN;
  }

  public static boolean isCdc(final JsonNode config) {
    final boolean isCdc = config.hasNonNull("replication_method")
        && config.get("replication_method").hasNonNull("replication_slot")
        && config.get("replication_method").hasNonNull("publication");
    LOGGER.info("using CDC: {}", isCdc);
    return isCdc;
  }

  public static Optional<Integer> getFirstRecordWaitSeconds(final JsonNode config) {
    final JsonNode replicationMethod = config.get("replication_method");
    if (replicationMethod != null && replicationMethod.has("initial_waiting_seconds")) {
      final int seconds = config.get("replication_method").get("initial_waiting_seconds").asInt();
      return Optional.of(seconds);
    }
    return Optional.empty();
  }

  public static void checkFirstRecordWaitTime(final JsonNode config) {
    final Optional<Integer> firstRecordWaitSeconds = getFirstRecordWaitSeconds(config);
    if (firstRecordWaitSeconds.isPresent() && firstRecordWaitSeconds.get() > MAX_FIRST_RECORD_WAIT_TIME.getSeconds()) {
      throw new IllegalArgumentException(String.format(
          "Initial waiting seconds cannot be larger than %d seconds for safety.",
          MAX_FIRST_RECORD_WAIT_TIME.getSeconds()));
    }
  }

  public static Duration getFirstRecordWaitTime(final JsonNode config) {
    Duration firstRecordWaitTime = DEFAULT_FIRST_RECORD_WAIT_TIME;

    final Optional<Integer> firstRecordWaitSeconds = getFirstRecordWaitSeconds(config);
    if (firstRecordWaitSeconds.isPresent()) {
      if (firstRecordWaitSeconds.get() > MAX_FIRST_RECORD_WAIT_TIME.getSeconds()) {
        LOGGER.warn("First record waiting time is overridden to {} minutes, which is the max time allowed for safety.",
            MAX_FIRST_RECORD_WAIT_TIME.toMinutes());
        firstRecordWaitTime = MAX_FIRST_RECORD_WAIT_TIME;
      } else {
        firstRecordWaitTime = Duration.ofSeconds(firstRecordWaitSeconds.get());
      }
    }

    LOGGER.info("First record waiting time: {} seconds", firstRecordWaitTime.getSeconds());
    return firstRecordWaitTime;
  }

}
