# ----------------------------------------
# Glue Data Catalog database
# ----------------------------------------

resource "aws_glue_catalog_database" "market_data" {
  name = "${replace(var.project_name, "-", "_")}_${var.environment}"

  description = "Glue catalog database for batch analytics tables"

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# ----------------------------------------
# Glue table for analytics/ohlc_daily
# ----------------------------------------

resource "aws_glue_catalog_table" "ohlc_daily" {
  name          = "ohlc_daily"
  database_name = aws_glue_catalog_database.market_data.name
  table_type    = "EXTERNAL_TABLE"

  parameters = {
    EXTERNAL = "TRUE"
  }

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.raw_bucket.bucket}/analytics/ohlc_daily/"
    input_format  = "org.apache.hadoop.mapred.TextInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.IgnoreKeyTextOutputFormat"

    ser_de_info {
      name                  = "ohlc_daily_json"
      serialization_library = "org.openx.data.jsonserde.JsonSerDe"
    }

    columns {
      name = "symbol"
      type = "string"
    }

    columns {
      name = "date"
      type = "string"
    }

    columns {
      name = "open"
      type = "double"
    }

    columns {
      name = "high"
      type = "double"
    }

    columns {
      name = "low"
      type = "double"
    }

    columns {
      name = "close"
      type = "double"
    }

    columns {
      name = "volume"
      type = "bigint"
    }

    columns {
      name = "currency"
      type = "string"
    }

    columns {
      name = "ts_market"
      type = "string"
    }

    columns {
      name = "ts_ingest"
      type = "string"
    }

    columns {
      name = "source"
      type = "string"
    }
  }
}