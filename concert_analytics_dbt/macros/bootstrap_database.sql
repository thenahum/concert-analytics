{% macro bootstrap_database() %}
    {#
      Rebuild-oriented warehouse bootstrap.

      This intentionally does not run on every dbt invocation. Call with:
          dbt run-operation bootstrap_database
    #}

    {% set bootstrap_sql %}
        create schema if not exists raw;
        create schema if not exists analytics_staging;
        create schema if not exists analytics_mart;
        create schema if not exists analytics_project;

        create extension if not exists pg_trgm with schema public;

        create or replace function analytics_mart.similarity(left_text text, right_text text)
        returns real
        language sql
        immutable
        parallel safe
        as $$
            select public.similarity(left_text, right_text)::real
        $$;
    {% endset %}

    {% do log("Bootstrapping Concert Analytics schemas and database functions", info=True) %}
    {% do run_query(bootstrap_sql) %}
    {% do log("Bootstrap complete", info=True) %}
{% endmacro %}
