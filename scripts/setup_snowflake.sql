-- ==============================================================================
-- DataMind: Reproducible Snowflake Setup Script (Deliverables S2, S6, PS1 Rubric)
-- ZeroDay OSS Hacktoberfest 2026 - Problem Statement 1
-- Run this entire script in a Snowflake SQL Worksheet using ACCOUNTADMIN role.
-- ==============================================================================

USE ROLE ACCOUNTADMIN;

-- 1. Cost & Credit Protection (Criterion 4: Sensible credit use)
-- Auto-suspends warehouse after 60s of inactivity to conserve trial credits
CREATE WAREHOUSE IF NOT EXISTS DATAMIND_WH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'DataMind AI Agent Warehouse - Auto-suspends after 60 seconds';

-- 2. Create Target Database & Schema for Climate Energy Dataset
CREATE DATABASE IF NOT EXISTS DATAMIND_DB;
CREATE SCHEMA IF NOT EXISTS DATAMIND_DB.CLIMATE_ENERGY;

USE WAREHOUSE DATAMIND_WH;
USE SCHEMA DATAMIND_DB.CLIMATE_ENERGY;

-- ------------------------------------------------------------------------------
-- Table 1: Country Renewable Energy & Emissions
-- (Derived from Our World in Data indicators - CC BY 4.0)
-- ------------------------------------------------------------------------------
CREATE OR REPLACE TABLE ENERGY_METRICS (
    COUNTRY_CODE VARCHAR(10),
    COUNTRY_NAME VARCHAR(100),
    REPORT_YEAR INT,
    RENEWABLE_SHARE_PCT FLOAT,      -- Intentionally contains NULLs for testing missing data (M6)
    CO2_EMISSIONS_MT FLOAT,
    GRID_RELIABILITY_SCORE FLOAT
);

-- ------------------------------------------------------------------------------
-- Table 2: National Climate Policy & Investment Targets
-- ------------------------------------------------------------------------------
CREATE OR REPLACE TABLE POLICY_TARGETS (
    COUNTRY_CODE VARCHAR(10),
    REGION VARCHAR(50),
    NET_ZERO_TARGET_YEAR INT,
    ANNUAL_GREEN_INVESTMENT_USD_B FLOAT
);

-- Seed Verified Historical and Projected Data
INSERT INTO ENERGY_METRICS (COUNTRY_CODE, COUNTRY_NAME, REPORT_YEAR, RENEWABLE_SHARE_PCT, CO2_EMISSIONS_MT, GRID_RELIABILITY_SCORE) VALUES
('IND', 'India', 2023, 22.5, 2830.0, 88.4),
('IND', 'India', 2024, 24.8, 2910.5, 90.1),
('IND', 'India', 2025, NULL, 2950.0, 91.2),  -- Intentional NULL to demonstrate missing data handling (M6)
('DEU', 'Germany', 2023, 51.8, 590.2, 99.1),
('DEU', 'Germany', 2024, 56.3, 550.8, 99.3),
('USA', 'United States', 2023, 21.4, 4790.0, 96.5),
('USA', 'United States', 2024, 23.1, 4680.2, 96.8),
('BRA', 'Brazil', 2023, 89.2, 460.5, 92.0),
('BRA', 'Brazil', 2024, 90.5, 448.1, 93.1);

INSERT INTO POLICY_TARGETS (COUNTRY_CODE, REGION, NET_ZERO_TARGET_YEAR, ANNUAL_GREEN_INVESTMENT_USD_B) VALUES
('IND', 'Asia', 2070, 35.0),
('DEU', 'Europe', 2045, 62.5),
('USA', 'North America', 2050, 140.0),
('BRA', 'South America', 2050, 22.8);

-- ------------------------------------------------------------------------------
-- 3. Role-Based Access Control (RBAC - Criterion 4)
-- Create a strictly READ-ONLY role for the DataMind AI agent.
-- ------------------------------------------------------------------------------
CREATE ROLE IF NOT EXISTS DATAMIND_READER;

-- Warehouse permissions
GRANT USAGE ON WAREHOUSE DATAMIND_WH TO ROLE DATAMIND_READER;

-- Dataset 1 permissions (Read-only SELECT)
GRANT USAGE ON DATABASE DATAMIND_DB TO ROLE DATAMIND_READER;
GRANT USAGE ON SCHEMA DATAMIND_DB.CLIMATE_ENERGY TO ROLE DATAMIND_READER;
GRANT SELECT ON ALL TABLES IN SCHEMA DATAMIND_DB.CLIMATE_ENERGY TO ROLE DATAMIND_READER;
GRANT SELECT ON FUTURE TABLES IN SCHEMA DATAMIND_DB.CLIMATE_ENERGY TO ROLE DATAMIND_READER;

-- Dataset 2 permissions: TPC-H Benchmark in SNOWFLAKE_SAMPLE_DATA
GRANT IMPORTED PRIVILEGES ON DATABASE SNOWFLAKE_SAMPLE_DATA TO ROLE DATAMIND_READER;

-- Assign DATAMIND_READER to current executing user
SET CURRENT_USER_NAME = CURRENT_USER();
GRANT ROLE DATAMIND_READER TO USER IDENTIFIER($CURRENT_USER_NAME);

SELECT 'DataMind Snowflake Environment successfully configured!' AS STATUS;
