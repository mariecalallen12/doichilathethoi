--
-- PostgreSQL database dump
--

\restrict GeNZflRIBa8FWiCmu8SqfRbabctay8tBxW4UbPFNXp9XspZRH4JE2kEciEtiDX3

-- Dumped from database version 15.15
-- Dumped by pg_dump version 15.15

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: aml_screenings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.aml_screenings (
    id integer NOT NULL,
    user_id integer NOT NULL,
    screening_type character varying(50) NOT NULL,
    status character varying(50) DEFAULT 'clean'::character varying,
    risk_level character varying(20) DEFAULT 'low'::character varying,
    findings jsonb DEFAULT '[]'::jsonb,
    sanctions_match boolean DEFAULT false,
    pep_match boolean DEFAULT false,
    adverse_media_match boolean DEFAULT false,
    watchlist_match boolean DEFAULT false,
    sources_checked character varying[] DEFAULT '{}'::character varying[],
    last_checked timestamp with time zone DEFAULT now(),
    next_review timestamp with time zone,
    reviewed_by integer,
    reviewed_at timestamp with time zone,
    reviewer_notes text,
    trigger_transaction_id integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.aml_screenings OWNER TO postgres;

--
-- Name: aml_screenings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.aml_screenings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.aml_screenings_id_seq OWNER TO postgres;

--
-- Name: aml_screenings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.aml_screenings_id_seq OWNED BY public.aml_screenings.id;


--
-- Name: analytics_events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.analytics_events (
    id integer NOT NULL,
    user_id integer,
    event_name character varying(100) NOT NULL,
    event_category character varying(50),
    event_label character varying(255),
    event_value integer,
    event_properties jsonb DEFAULT '{}'::jsonb,
    session_id character varying(255),
    page_url character varying(500),
    referrer character varying(500),
    ip_address inet,
    user_agent text,
    device_type character varying(50),
    browser character varying(100),
    os character varying(100),
    country character varying(100),
    city character varying(100),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.analytics_events OWNER TO postgres;

--
-- Name: analytics_events_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.analytics_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.analytics_events_id_seq OWNER TO postgres;

--
-- Name: analytics_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.analytics_events_id_seq OWNED BY public.analytics_events.id;


--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_logs (
    id integer NOT NULL,
    user_id integer,
    user_role character varying(50),
    action character varying(100) NOT NULL,
    resource_type character varying(100) NOT NULL,
    resource_id character varying(255),
    old_values jsonb,
    new_values jsonb,
    ip_address inet,
    user_agent text,
    session_id character varying(255),
    result character varying(50) DEFAULT 'success'::character varying,
    error_message text,
    category character varying(50),
    severity character varying(20) DEFAULT 'info'::character varying,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.audit_logs OWNER TO postgres;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.audit_logs_id_seq OWNER TO postgres;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.audit_logs_id_seq OWNED BY public.audit_logs.id;


--
-- Name: compliance_events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.compliance_events (
    id integer NOT NULL,
    user_id integer,
    event_type character varying(100) NOT NULL,
    severity character varying(50) DEFAULT 'medium'::character varying,
    status character varying(50) DEFAULT 'open'::character varying,
    title character varying(255),
    description text NOT NULL,
    risk_score integer DEFAULT 0,
    risk_factors jsonb DEFAULT '[]'::jsonb,
    assigned_to integer,
    escalated boolean DEFAULT false,
    escalated_to integer,
    escalated_at timestamp with time zone,
    resolved_by integer,
    resolved_at timestamp with time zone,
    resolution_notes text,
    resolution_action character varying(100),
    evidence jsonb DEFAULT '{}'::jsonb,
    related_transaction_id integer,
    related_order_id integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.compliance_events OWNER TO postgres;

--
-- Name: compliance_events_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.compliance_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.compliance_events_id_seq OWNER TO postgres;

--
-- Name: compliance_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.compliance_events_id_seq OWNED BY public.compliance_events.id;


--
-- Name: exchange_rates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exchange_rates (
    id integer NOT NULL,
    base_asset character varying(20) NOT NULL,
    target_asset character varying(20) NOT NULL,
    rate numeric(20,8) NOT NULL,
    inverse_rate numeric(20,8),
    is_active boolean DEFAULT true,
    priority integer DEFAULT 0,
    source character varying(50),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.exchange_rates OWNER TO postgres;

--
-- Name: exchange_rates_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.exchange_rates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.exchange_rates_id_seq OWNER TO postgres;

--
-- Name: exchange_rates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.exchange_rates_id_seq OWNED BY public.exchange_rates.id;


--
-- Name: iceberg_orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.iceberg_orders (
    id integer NOT NULL,
    user_id integer NOT NULL,
    parent_order_id integer,
    symbol character varying(20) NOT NULL,
    side character varying(10) NOT NULL,
    total_quantity numeric(20,8) NOT NULL,
    slice_quantity numeric(20,8) NOT NULL,
    remaining_quantity numeric(20,8) NOT NULL,
    price numeric(20,8),
    status character varying(50) DEFAULT 'active'::character varying,
    slices_completed integer DEFAULT 0,
    total_filled numeric(20,8) DEFAULT '0'::numeric,
    average_fill_price numeric(20,8),
    completed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.iceberg_orders OWNER TO postgres;

--
-- Name: iceberg_orders_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.iceberg_orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.iceberg_orders_id_seq OWNER TO postgres;

--
-- Name: iceberg_orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.iceberg_orders_id_seq OWNED BY public.iceberg_orders.id;


--
-- Name: kyc_documents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.kyc_documents (
    id integer NOT NULL,
    user_id integer NOT NULL,
    document_type character varying(50) NOT NULL,
    document_number character varying(100),
    document_file_url character varying(500),
    file_hash character varying(255),
    issue_date date,
    expiry_date date,
    issuing_authority character varying(255),
    issuing_country character varying(100),
    verification_status character varying(50) DEFAULT 'pending'::character varying,
    verified_by integer,
    verification_date timestamp with time zone,
    rejection_reason text,
    ai_verification_score numeric(5,2),
    ai_verification_details jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.kyc_documents OWNER TO postgres;

--
-- Name: kyc_documents_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.kyc_documents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.kyc_documents_id_seq OWNER TO postgres;

--
-- Name: kyc_documents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.kyc_documents_id_seq OWNED BY public.kyc_documents.id;


--
-- Name: market_analysis; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.market_analysis (
    id integer NOT NULL,
    symbol character varying(20) NOT NULL,
    analysis_type character varying(50) NOT NULL,
    indicators jsonb DEFAULT '{}'::jsonb,
    signals jsonb DEFAULT '[]'::jsonb,
    sentiment_score numeric(5,2),
    price_prediction jsonb DEFAULT '{}'::jsonb,
    confidence_score numeric(5,2),
    timeframe character varying(10) NOT NULL,
    analysis_date timestamp with time zone NOT NULL,
    source character varying(50),
    metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.market_analysis OWNER TO postgres;

--
-- Name: market_analysis_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.market_analysis_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.market_analysis_id_seq OWNER TO postgres;

--
-- Name: market_analysis_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.market_analysis_id_seq OWNED BY public.market_analysis.id;


--
-- Name: market_data_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.market_data_history (
    id integer NOT NULL,
    symbol character varying(20) NOT NULL,
    base_asset character varying(20) NOT NULL,
    quote_asset character varying(20) NOT NULL,
    open_price numeric(20,8) NOT NULL,
    high_price numeric(20,8) NOT NULL,
    low_price numeric(20,8) NOT NULL,
    close_price numeric(20,8) NOT NULL,
    volume numeric(20,8) NOT NULL,
    timeframe character varying(10) NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    number_of_trades integer DEFAULT 0,
    taker_buy_volume numeric(20,8),
    taker_sell_volume numeric(20,8),
    source character varying(50),
    metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.market_data_history OWNER TO postgres;

--
-- Name: market_data_history_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.market_data_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.market_data_history_id_seq OWNER TO postgres;

--
-- Name: market_data_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.market_data_history_id_seq OWNED BY public.market_data_history.id;


--
-- Name: market_prices; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.market_prices (
    id integer NOT NULL,
    symbol character varying(20) NOT NULL,
    base_asset character varying(20) NOT NULL,
    quote_asset character varying(20) NOT NULL,
    price numeric(20,8) NOT NULL,
    price_change_24h numeric(20,8),
    price_change_percent_24h numeric(10,4),
    volume_24h numeric(20,8),
    quote_volume_24h numeric(20,8),
    high_24h numeric(20,8),
    low_24h numeric(20,8),
    last_update timestamp with time zone NOT NULL,
    is_active boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.market_prices OWNER TO postgres;

--
-- Name: market_prices_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.market_prices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.market_prices_id_seq OWNER TO postgres;

--
-- Name: market_prices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.market_prices_id_seq OWNED BY public.market_prices.id;


--
-- Name: oco_orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.oco_orders (
    id integer NOT NULL,
    user_id integer NOT NULL,
    primary_order_id integer,
    secondary_order_id integer,
    symbol character varying(20) NOT NULL,
    primary_side character varying(10),
    secondary_side character varying(10),
    status character varying(50) DEFAULT 'active'::character varying,
    triggered_order_id integer,
    cancelled_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.oco_orders OWNER TO postgres;

--
-- Name: oco_orders_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.oco_orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.oco_orders_id_seq OWNER TO postgres;

--
-- Name: oco_orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.oco_orders_id_seq OWNED BY public.oco_orders.id;


--
-- Name: permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.permissions (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    resource character varying(100) NOT NULL,
    action character varying(100) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.permissions OWNER TO postgres;

--
-- Name: permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.permissions_id_seq OWNER TO postgres;

--
-- Name: permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.permissions_id_seq OWNED BY public.permissions.id;


--
-- Name: portfolio_positions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.portfolio_positions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    symbol character varying(20) NOT NULL,
    quantity numeric(20,8) NOT NULL,
    average_price numeric(20,8) NOT NULL,
    market_value numeric(20,8),
    unrealized_pnl numeric(20,8),
    realized_pnl numeric(20,8) DEFAULT '0'::numeric,
    position_type character varying(20) DEFAULT 'long'::character varying,
    entry_price numeric(20,8),
    entry_time timestamp with time zone DEFAULT now(),
    leverage numeric(10,2) DEFAULT '1'::numeric,
    margin_used numeric(20,8) DEFAULT '0'::numeric,
    is_closed boolean DEFAULT false,
    closed_at timestamp with time zone,
    closed_price numeric(20,8),
    closed_reason character varying(100),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.portfolio_positions OWNER TO postgres;

--
-- Name: portfolio_positions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.portfolio_positions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.portfolio_positions_id_seq OWNER TO postgres;

--
-- Name: portfolio_positions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.portfolio_positions_id_seq OWNED BY public.portfolio_positions.id;


--
-- Name: referral_codes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.referral_codes (
    id integer NOT NULL,
    staff_id integer NOT NULL,
    code character varying(50) NOT NULL,
    token character varying(255) NOT NULL,
    status character varying(50) DEFAULT 'active'::character varying,
    max_uses integer,
    used_count integer DEFAULT 0,
    expires_at timestamp with time zone,
    commission_rate integer DEFAULT 10,
    commission_type character varying(50) DEFAULT 'percentage'::character varying,
    created_by integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.referral_codes OWNER TO postgres;

--
-- Name: referral_codes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.referral_codes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.referral_codes_id_seq OWNER TO postgres;

--
-- Name: referral_codes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.referral_codes_id_seq OWNED BY public.referral_codes.id;


--
-- Name: referral_registrations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.referral_registrations (
    id integer NOT NULL,
    referral_code_id integer NOT NULL,
    referred_user_id integer NOT NULL,
    source_type character varying(20) NOT NULL,
    source_url character varying(500),
    ip_address inet,
    user_agent text,
    status character varying(50) DEFAULT 'pending'::character varying,
    commission_paid boolean DEFAULT false,
    commission_amount integer DEFAULT 0,
    commission_paid_at timestamp with time zone,
    verified_at timestamp with time zone,
    first_deposit_at timestamp with time zone,
    first_trade_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.referral_registrations OWNER TO postgres;

--
-- Name: referral_registrations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.referral_registrations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.referral_registrations_id_seq OWNER TO postgres;

--
-- Name: referral_registrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.referral_registrations_id_seq OWNED BY public.referral_registrations.id;


--
-- Name: refresh_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.refresh_tokens (
    id integer NOT NULL,
    user_id integer NOT NULL,
    token character varying(500) NOT NULL,
    token_hash character varying(255) NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    revoked boolean DEFAULT false,
    revoked_at timestamp with time zone,
    device_id character varying(255),
    user_agent text,
    ip_address character varying(50),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.refresh_tokens OWNER TO postgres;

--
-- Name: refresh_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.refresh_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.refresh_tokens_id_seq OWNER TO postgres;

--
-- Name: refresh_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.refresh_tokens_id_seq OWNED BY public.refresh_tokens.id;


--
-- Name: risk_assessments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.risk_assessments (
    id integer NOT NULL,
    user_id integer NOT NULL,
    assessment_type character varying(50) NOT NULL,
    risk_level character varying(20) NOT NULL,
    risk_score integer NOT NULL,
    assessment_data jsonb DEFAULT '{}'::jsonb,
    factors_considered character varying[] DEFAULT '{}'::character varying[],
    recommendations text,
    assessed_by integer,
    assessment_method character varying(50) DEFAULT 'automated'::character varying,
    next_review_date date,
    status character varying(50) DEFAULT 'active'::character varying,
    previous_assessment_id integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.risk_assessments OWNER TO postgres;

--
-- Name: risk_assessments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.risk_assessments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.risk_assessments_id_seq OWNER TO postgres;

--
-- Name: risk_assessments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.risk_assessments_id_seq OWNED BY public.risk_assessments.id;


--
-- Name: role_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.role_permissions (
    id integer NOT NULL,
    role_id integer NOT NULL,
    permission_id integer NOT NULL,
    granted_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.role_permissions OWNER TO postgres;

--
-- Name: role_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.role_permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.role_permissions_id_seq OWNER TO postgres;

--
-- Name: role_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.role_permissions_id_seq OWNED BY public.role_permissions.id;


--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description text,
    is_system_role boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.roles_id_seq OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: system_settings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.system_settings (
    id integer NOT NULL,
    key character varying(255) NOT NULL,
    value jsonb NOT NULL,
    description text,
    is_public boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.system_settings OWNER TO postgres;

--
-- Name: system_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.system_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.system_settings_id_seq OWNER TO postgres;

--
-- Name: system_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.system_settings_id_seq OWNED BY public.system_settings.id;


--
-- Name: trading_bots; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trading_bots (
    id integer NOT NULL,
    user_id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    strategy_id character varying(100),
    strategy_name character varying(255),
    strategy_parameters jsonb DEFAULT '{}'::jsonb,
    symbols character varying[] DEFAULT '{}'::character varying[],
    base_amount numeric(20,8) DEFAULT '0'::numeric,
    leverage numeric(10,2) DEFAULT '1'::numeric,
    max_positions integer DEFAULT 5,
    risk_per_trade numeric(5,2) DEFAULT '1'::numeric,
    status character varying(50) DEFAULT 'PAUSED'::character varying,
    last_run_at timestamp with time zone,
    next_run_at timestamp with time zone,
    total_trades integer DEFAULT 0,
    winning_trades integer DEFAULT 0,
    losing_trades integer DEFAULT 0,
    total_pnl numeric(20,8) DEFAULT '0'::numeric,
    max_drawdown numeric(20,8) DEFAULT '0'::numeric,
    logs jsonb DEFAULT '[]'::jsonb,
    error_count integer DEFAULT 0,
    last_error text,
    last_error_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.trading_bots OWNER TO postgres;

--
-- Name: trading_bots_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trading_bots_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trading_bots_id_seq OWNER TO postgres;

--
-- Name: trading_bots_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trading_bots_id_seq OWNED BY public.trading_bots.id;


--
-- Name: trading_orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trading_orders (
    id integer NOT NULL,
    user_id integer NOT NULL,
    order_type character varying(50) NOT NULL,
    symbol character varying(20) NOT NULL,
    side character varying(10) NOT NULL,
    quantity numeric(20,8) NOT NULL,
    price numeric(20,8),
    stop_price numeric(20,8),
    time_in_force character varying(10) DEFAULT 'GTC'::character varying,
    status character varying(50) DEFAULT 'pending'::character varying,
    filled_quantity numeric(20,8) DEFAULT '0'::numeric,
    filled_price numeric(20,8),
    remaining_quantity numeric(20,8),
    average_price numeric(20,8),
    commission numeric(20,8) DEFAULT '0'::numeric,
    source character varying(100),
    ip_address inet,
    user_agent text,
    filled_at timestamp with time zone,
    cancelled_at timestamp with time zone,
    expires_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.trading_orders OWNER TO postgres;

--
-- Name: trading_orders_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trading_orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trading_orders_id_seq OWNER TO postgres;

--
-- Name: trading_orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trading_orders_id_seq OWNED BY public.trading_orders.id;


--
-- Name: trailing_stop_orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trailing_stop_orders (
    id integer NOT NULL,
    user_id integer NOT NULL,
    parent_order_id integer,
    symbol character varying(20) NOT NULL,
    side character varying(10) NOT NULL,
    quantity numeric(20,8) NOT NULL,
    stop_type character varying(20),
    stop_value numeric(20,8),
    trailing_distance numeric(20,8),
    current_stop_price numeric(20,8),
    activation_price numeric(20,8),
    highest_price numeric(20,8),
    lowest_price numeric(20,8),
    status character varying(50) DEFAULT 'active'::character varying,
    triggered_at timestamp with time zone,
    completed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.trailing_stop_orders OWNER TO postgres;

--
-- Name: trailing_stop_orders_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trailing_stop_orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trailing_stop_orders_id_seq OWNER TO postgres;

--
-- Name: trailing_stop_orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trailing_stop_orders_id_seq OWNED BY public.trailing_stop_orders.id;


--
-- Name: transactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.transactions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    transaction_type character varying(50) NOT NULL,
    category character varying(50),
    asset character varying(20) NOT NULL,
    amount numeric(20,8) NOT NULL,
    fee numeric(20,8) DEFAULT '0'::numeric,
    net_amount numeric(20,8) NOT NULL,
    balance_before numeric(20,8),
    balance_after numeric(20,8),
    status character varying(50) DEFAULT 'pending'::character varying,
    reference_id character varying(100),
    external_id character varying(100),
    description text,
    bank_account character varying(50),
    bank_name character varying(100),
    transaction_hash character varying(255),
    from_address character varying(255),
    to_address character varying(255),
    network character varying(50),
    confirmations integer DEFAULT 0,
    metadata jsonb DEFAULT '{}'::jsonb,
    ip_address inet,
    completed_at timestamp with time zone,
    cancelled_at timestamp with time zone,
    failed_reason text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.transactions OWNER TO postgres;

--
-- Name: transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.transactions_id_seq OWNER TO postgres;

--
-- Name: transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.transactions_id_seq OWNED BY public.transactions.id;


--
-- Name: user_profiles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_profiles (
    id integer NOT NULL,
    user_id integer NOT NULL,
    full_name character varying(255),
    display_name character varying(100),
    date_of_birth date,
    phone character varying(20),
    address text,
    country character varying(100),
    city character varying(100),
    postal_code character varying(20),
    id_type character varying(50),
    id_number character varying(100),
    id_verified boolean DEFAULT false,
    id_front_url character varying(500),
    id_back_url character varying(500),
    selfie_url character varying(500),
    bank_account_name character varying(255),
    bank_account_number character varying(50),
    bank_name character varying(100),
    bank_branch character varying(100),
    emergency_contact_name character varying(255),
    emergency_contact_phone character varying(20),
    preferences jsonb DEFAULT '{}'::jsonb,
    notification_settings jsonb DEFAULT '{"sms": false, "push": true, "email": true}'::jsonb,
    avatar_url character varying(500),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.user_profiles OWNER TO postgres;

--
-- Name: user_profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_profiles_id_seq OWNER TO postgres;

--
-- Name: user_profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_profiles_id_seq OWNED BY public.user_profiles.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role_id integer,
    status character varying(50) DEFAULT 'pending'::character varying,
    email_verified boolean DEFAULT false,
    phone_verified boolean DEFAULT false,
    kyc_status character varying(50) DEFAULT 'pending'::character varying,
    customer_payment_id character varying(50),
    referral_code character varying(50),
    referred_by integer,
    last_login_at timestamp with time zone,
    failed_login_attempts integer DEFAULT 0,
    account_locked_until timestamp with time zone,
    terms_accepted_at timestamp with time zone,
    privacy_accepted_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: wallet_balances; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.wallet_balances (
    id integer NOT NULL,
    user_id integer NOT NULL,
    asset character varying(20) NOT NULL,
    available_balance numeric(20,8) DEFAULT '0'::numeric NOT NULL,
    locked_balance numeric(20,8) DEFAULT '0'::numeric NOT NULL,
    pending_balance numeric(20,8) DEFAULT '0'::numeric NOT NULL,
    reserved_balance numeric(20,8) DEFAULT '0'::numeric NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.wallet_balances OWNER TO postgres;

--
-- Name: wallet_balances_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.wallet_balances_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.wallet_balances_id_seq OWNER TO postgres;

--
-- Name: wallet_balances_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.wallet_balances_id_seq OWNED BY public.wallet_balances.id;


--
-- Name: watchlists; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.watchlists (
    id integer NOT NULL,
    user_id integer NOT NULL,
    name character varying(255) DEFAULT 'Default'::character varying,
    description text,
    symbols character varying[] DEFAULT '{}'::character varying[],
    is_default boolean DEFAULT false,
    is_public boolean DEFAULT false,
    sort_order integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.watchlists OWNER TO postgres;

--
-- Name: watchlists_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.watchlists_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.watchlists_id_seq OWNER TO postgres;

--
-- Name: watchlists_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.watchlists_id_seq OWNED BY public.watchlists.id;


--
-- Name: aml_screenings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.aml_screenings ALTER COLUMN id SET DEFAULT nextval('public.aml_screenings_id_seq'::regclass);


--
-- Name: analytics_events id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analytics_events ALTER COLUMN id SET DEFAULT nextval('public.analytics_events_id_seq'::regclass);


--
-- Name: audit_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs ALTER COLUMN id SET DEFAULT nextval('public.audit_logs_id_seq'::regclass);


--
-- Name: compliance_events id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compliance_events ALTER COLUMN id SET DEFAULT nextval('public.compliance_events_id_seq'::regclass);


--
-- Name: exchange_rates id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exchange_rates ALTER COLUMN id SET DEFAULT nextval('public.exchange_rates_id_seq'::regclass);


--
-- Name: iceberg_orders id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.iceberg_orders ALTER COLUMN id SET DEFAULT nextval('public.iceberg_orders_id_seq'::regclass);


--
-- Name: kyc_documents id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kyc_documents ALTER COLUMN id SET DEFAULT nextval('public.kyc_documents_id_seq'::regclass);


--
-- Name: market_analysis id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.market_analysis ALTER COLUMN id SET DEFAULT nextval('public.market_analysis_id_seq'::regclass);


--
-- Name: market_data_history id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.market_data_history ALTER COLUMN id SET DEFAULT nextval('public.market_data_history_id_seq'::regclass);


--
-- Name: market_prices id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.market_prices ALTER COLUMN id SET DEFAULT nextval('public.market_prices_id_seq'::regclass);


--
-- Name: oco_orders id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.oco_orders ALTER COLUMN id SET DEFAULT nextval('public.oco_orders_id_seq'::regclass);


--
-- Name: permissions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions ALTER COLUMN id SET DEFAULT nextval('public.permissions_id_seq'::regclass);


--
-- Name: portfolio_positions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.portfolio_positions ALTER COLUMN id SET DEFAULT nextval('public.portfolio_positions_id_seq'::regclass);


--
-- Name: referral_codes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.referral_codes ALTER COLUMN id SET DEFAULT nextval('public.referral_codes_id_seq'::regclass);


--
-- Name: referral_registrations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.referral_registrations ALTER COLUMN id SET DEFAULT nextval('public.referral_registrations_id_seq'::regclass);


--
-- Name: refresh_tokens id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.refresh_tokens ALTER COLUMN id SET DEFAULT nextval('public.refresh_tokens_id_seq'::regclass);


--
-- Name: risk_assessments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.risk_assessments ALTER COLUMN id SET DEFAULT nextval('public.risk_assessments_id_seq'::regclass);


--
-- Name: role_permissions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions ALTER COLUMN id SET DEFAULT nextval('public.role_permissions_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: system_settings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_settings ALTER COLUMN id SET DEFAULT nextval('public.system_settings_id_seq'::regclass);


--
-- Name: trading_bots id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trading_bots ALTER COLUMN id SET DEFAULT nextval('public.trading_bots_id_seq'::regclass);


--
-- Name: trading_orders id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trading_orders ALTER COLUMN id SET DEFAULT nextval('public.trading_orders_id_seq'::regclass);


--
-- Name: trailing_stop_orders id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trailing_stop_orders ALTER COLUMN id SET DEFAULT nextval('public.trailing_stop_orders_id_seq'::regclass);


--
-- Name: transactions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions ALTER COLUMN id SET DEFAULT nextval('public.transactions_id_seq'::regclass);


--
-- Name: user_profiles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_profiles ALTER COLUMN id SET DEFAULT nextval('public.user_profiles_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: wallet_balances id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.wallet_balances ALTER COLUMN id SET DEFAULT nextval('public.wallet_balances_id_seq'::regclass);


--
-- Name: watchlists id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.watchlists ALTER COLUMN id SET DEFAULT nextval('public.watchlists_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
004_add_system_settings
\.


--
-- Data for Name: aml_screenings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.aml_screenings (id, user_id, screening_type, status, risk_level, findings, sanctions_match, pep_match, adverse_media_match, watchlist_match, sources_checked, last_checked, next_review, reviewed_by, reviewed_at, reviewer_notes, trigger_transaction_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: analytics_events; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.analytics_events (id, user_id, event_name, event_category, event_label, event_value, event_properties, session_id, page_url, referrer, ip_address, user_agent, device_type, browser, os, country, city, created_at) FROM stdin;
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.audit_logs (id, user_id, user_role, action, resource_type, resource_id, old_values, new_values, ip_address, user_agent, session_id, result, error_message, category, severity, created_at) FROM stdin;
1	\N	\N	login_failed	user	\N	\N	\N	172.18.0.1	python-requests/2.32.5	\N	failure	Invalid credentials	authentication	info	2025-12-06 12:08:37.830653+00
2	\N	\N	login_failed	user	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Cursor/2.1.49 Chrome/138.0.7204.251 Electron/37.7.0 Safari/537.36	\N	failure	Invalid credentials	authentication	info	2025-12-06 14:47:36.746056+00
3	\N	\N	login_failed	user	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Cursor/2.1.49 Chrome/138.0.7204.251 Electron/37.7.0 Safari/537.36	\N	failure	Invalid credentials	authentication	info	2025-12-06 14:54:21.834562+00
4	\N	\N	login_failed	user	\N	\N	\N	172.18.0.1	curl/7.81.0	\N	failure	Invalid credentials	authentication	info	2025-12-06 14:55:05.620204+00
5	\N	\N	login_failed	user	\N	\N	\N	172.18.0.1	curl/7.81.0	\N	failure	Invalid credentials	authentication	info	2025-12-06 14:59:06.620678+00
6	\N	\N	login_failed	user	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Cursor/2.1.49 Chrome/138.0.7204.251 Electron/37.7.0 Safari/537.36	\N	failure	Invalid credentials	authentication	info	2025-12-06 14:59:47.53854+00
7	1	\N	login	user	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Cursor/2.1.49 Chrome/138.0.7204.251 Electron/37.7.0 Safari/537.36	\N	success	\N	authentication	info	2025-12-06 15:03:13.727161+00
8	1	\N	get_users	admin	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Cursor/2.1.49 Chrome/138.0.7204.251 Electron/37.7.0 Safari/537.36	\N	success	\N	admin	info	2025-12-06 15:19:56.69665+00
9	1	\N	get_admin_trades	admin	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Cursor/2.1.49 Chrome/138.0.7204.251 Electron/37.7.0 Safari/537.36	\N	success	\N	admin	info	2025-12-06 15:25:07.374277+00
10	1	\N	get_admin_trades	admin	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Cursor/2.1.49 Chrome/138.0.7204.251 Electron/37.7.0 Safari/537.36	\N	success	\N	admin	info	2025-12-06 15:26:14.009185+00
11	1	\N	login	user	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Cursor/2.1.49 Chrome/138.0.7204.251 Electron/37.7.0 Safari/537.36	\N	success	\N	authentication	info	2025-12-06 16:16:47.493174+00
12	\N	\N	login_failed	user	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36	\N	failure	Invalid credentials	authentication	info	2025-12-06 16:20:07.186027+00
13	1	\N	get_users	admin	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Cursor/2.1.49 Chrome/138.0.7204.251 Electron/37.7.0 Safari/537.36	\N	success	\N	admin	info	2025-12-06 16:24:58.901352+00
14	1	\N	login	user	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Cursor/2.1.49 Chrome/138.0.7204.251 Electron/37.7.0 Safari/537.36	\N	success	\N	authentication	info	2025-12-06 20:59:21.088916+00
15	1	\N	get_users	admin	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Cursor/2.1.49 Chrome/138.0.7204.251 Electron/37.7.0 Safari/537.36	\N	success	\N	admin	info	2025-12-06 21:05:18.345494+00
16	1	\N	get_admin_trades	admin	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Cursor/2.1.49 Chrome/138.0.7204.251 Electron/37.7.0 Safari/537.36	\N	success	\N	admin	info	2025-12-06 21:06:48.371638+00
17	1	\N	get_admin_trades	admin	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Cursor/2.1.49 Chrome/138.0.7204.251 Electron/37.7.0 Safari/537.36	\N	success	\N	admin	info	2025-12-06 21:09:39.607603+00
18	1	\N	get_users	admin	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Cursor/2.1.49 Chrome/138.0.7204.251 Electron/37.7.0 Safari/537.36	\N	success	\N	admin	info	2025-12-06 21:09:41.935809+00
19	1	\N	get_admin_trades	admin	\N	\N	\N	172.18.0.1	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Cursor/2.1.49 Chrome/138.0.7204.251 Electron/37.7.0 Safari/537.36	\N	success	\N	admin	info	2025-12-06 21:18:19.456618+00
\.


--
-- Data for Name: compliance_events; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.compliance_events (id, user_id, event_type, severity, status, title, description, risk_score, risk_factors, assigned_to, escalated, escalated_to, escalated_at, resolved_by, resolved_at, resolution_notes, resolution_action, evidence, related_transaction_id, related_order_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: exchange_rates; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exchange_rates (id, base_asset, target_asset, rate, inverse_rate, is_active, priority, source, created_at, updated_at) FROM stdin;
1	USD	VND	25000.00000000	0.00004000	t	1	internal	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
2	VND	USD	0.00004000	25000.00000000	t	1	internal	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
3	USDT	USD	1.00000000	1.00000000	t	1	internal	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
4	USD	USDT	1.00000000	1.00000000	t	1	internal	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
5	BTC	USD	45000.00000000	0.00002200	t	1	internal	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
6	ETH	USD	2500.00000000	0.00040000	t	1	internal	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
\.


--
-- Data for Name: iceberg_orders; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.iceberg_orders (id, user_id, parent_order_id, symbol, side, total_quantity, slice_quantity, remaining_quantity, price, status, slices_completed, total_filled, average_fill_price, completed_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: kyc_documents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.kyc_documents (id, user_id, document_type, document_number, document_file_url, file_hash, issue_date, expiry_date, issuing_authority, issuing_country, verification_status, verified_by, verification_date, rejection_reason, ai_verification_score, ai_verification_details, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: market_analysis; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.market_analysis (id, symbol, analysis_type, indicators, signals, sentiment_score, price_prediction, confidence_score, timeframe, analysis_date, source, metadata, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: market_data_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.market_data_history (id, symbol, base_asset, quote_asset, open_price, high_price, low_price, close_price, volume, timeframe, "timestamp", number_of_trades, taker_buy_volume, taker_sell_volume, source, metadata, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: market_prices; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.market_prices (id, symbol, base_asset, quote_asset, price, price_change_24h, price_change_percent_24h, volume_24h, quote_volume_24h, high_24h, low_24h, last_update, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: oco_orders; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.oco_orders (id, user_id, primary_order_id, secondary_order_id, symbol, primary_side, secondary_side, status, triggered_order_id, cancelled_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.permissions (id, name, description, resource, action, created_at, updated_at) FROM stdin;
1	users.view	Xem danh sách người dùng	users	view	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
2	users.create	Tạo người dùng mới	users	create	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
3	users.update	Cập nhật thông tin người dùng	users	update	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
4	users.delete	Xóa người dùng	users	delete	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
5	users.manage_roles	Quản lý vai trò người dùng	users	manage_roles	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
10	trading.view	Xem giao dịch	trading	view	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
11	trading.create	Tạo lệnh giao dịch	trading	create	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
12	trading.cancel	Hủy lệnh giao dịch	trading	cancel	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
13	trading.manage	Quản lý giao dịch (admin)	trading	manage	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
20	financial.view	Xem giao dịch tài chính	financial	view	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
21	financial.deposit	Nạp tiền	financial	deposit	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
22	financial.withdraw	Rút tiền	financial	withdraw	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
23	financial.approve	Duyệt giao dịch tài chính	financial	approve	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
30	admin.dashboard	Truy cập dashboard admin	admin	dashboard	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
31	admin.analytics	Xem analytics	admin	analytics	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
32	admin.reports	Xem báo cáo	admin	reports	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
33	admin.settings	Quản lý cài đặt hệ thống	admin	settings	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
34	admin.logs	Xem audit logs	admin	logs	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
40	compliance.kyc	Quản lý KYC	compliance	kyc	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
41	compliance.aml	Quản lý AML	compliance	aml	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
42	compliance.risk	Đánh giá rủi ro	compliance	risk	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
\.


--
-- Data for Name: portfolio_positions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.portfolio_positions (id, user_id, symbol, quantity, average_price, market_value, unrealized_pnl, realized_pnl, position_type, entry_price, entry_time, leverage, margin_used, is_closed, closed_at, closed_price, closed_reason, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: referral_codes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.referral_codes (id, staff_id, code, token, status, max_uses, used_count, expires_at, commission_rate, commission_type, created_by, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: referral_registrations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.referral_registrations (id, referral_code_id, referred_user_id, source_type, source_url, ip_address, user_agent, status, commission_paid, commission_amount, commission_paid_at, verified_at, first_deposit_at, first_trade_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: refresh_tokens; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.refresh_tokens (id, user_id, token, token_hash, expires_at, revoked, revoked_at, device_id, user_agent, ip_address, created_at, updated_at) FROM stdin;
1	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJhZG1pbkBkaWdpdGFsdXRvcGlhLmNvbSIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc2NTYzODE5MywiaWF0IjoxNzY1MDMzMzkzLCJ0eXBlIjoicmVmcmVzaCJ9.JCLUdyOPCp1pqGTUXeGvFEAigL7Oa2BEXtX6UDmg3OY	1c852b9107460ba01821ba1e79f2ed012d095fcd623450020ccc7ba9bde77f7b	2025-12-13 15:03:13.707532+00	f	\N	\N	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Cursor/2.1.49 Chrome/138.0.7204.251 Electron/37.7.0 Safari/537.36	172.18.0.1	2025-12-06 15:03:13.64906+00	2025-12-06 15:03:13.64906+00
2	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJhZG1pbkBkaWdpdGFsdXRvcGlhLmNvbSIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc2NTY0MjYwNywiaWF0IjoxNzY1MDM3ODA3LCJ0eXBlIjoicmVmcmVzaCJ9.LvPZ2EsdMFatnEUHMfu_NF2TkuJIuz8FxXTfLkORkGg	a7bff316e620b4fc77862d8ed43e4e7ce52f16d0e2b3f5577d76a71c9078ad38	2025-12-13 16:16:47.473925+00	f	\N	\N	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Cursor/2.1.49 Chrome/138.0.7204.251 Electron/37.7.0 Safari/537.36	172.18.0.1	2025-12-06 16:16:47.458291+00	2025-12-06 16:16:47.458291+00
3	1	eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJhZG1pbkBkaWdpdGFsdXRvcGlhLmNvbSIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc2NTY1OTU2MSwiaWF0IjoxNzY1MDU0NzYxLCJ0eXBlIjoicmVmcmVzaCJ9.NRNAeViTQxrvFVc62s9Uod67lDREe80Hdw79pEtfuB0	04198693179aa455066fcdc6eb18ee93eeacf30a6557fb1070cfe0856646d67a	2025-12-13 20:59:21.063415+00	f	\N	\N	Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Cursor/2.1.49 Chrome/138.0.7204.251 Electron/37.7.0 Safari/537.36	172.18.0.1	2025-12-06 20:59:21.049963+00	2025-12-06 20:59:21.049963+00
\.


--
-- Data for Name: risk_assessments; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.risk_assessments (id, user_id, assessment_type, risk_level, risk_score, assessment_data, factors_considered, recommendations, assessed_by, assessment_method, next_review_date, status, previous_assessment_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: role_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.role_permissions (id, role_id, permission_id, granted_at) FROM stdin;
1	1	1	2025-12-06 11:46:37.5691+00
2	1	2	2025-12-06 11:46:37.5691+00
3	1	3	2025-12-06 11:46:37.5691+00
4	1	4	2025-12-06 11:46:37.5691+00
5	1	5	2025-12-06 11:46:37.5691+00
6	1	10	2025-12-06 11:46:37.5691+00
7	1	11	2025-12-06 11:46:37.5691+00
8	1	12	2025-12-06 11:46:37.5691+00
9	1	13	2025-12-06 11:46:37.5691+00
10	1	20	2025-12-06 11:46:37.5691+00
11	1	21	2025-12-06 11:46:37.5691+00
12	1	22	2025-12-06 11:46:37.5691+00
13	1	23	2025-12-06 11:46:37.5691+00
14	1	30	2025-12-06 11:46:37.5691+00
15	1	31	2025-12-06 11:46:37.5691+00
16	1	32	2025-12-06 11:46:37.5691+00
17	1	33	2025-12-06 11:46:37.5691+00
18	1	34	2025-12-06 11:46:37.5691+00
19	1	40	2025-12-06 11:46:37.5691+00
20	1	41	2025-12-06 11:46:37.5691+00
21	1	42	2025-12-06 11:46:37.5691+00
22	2	1	2025-12-06 11:46:37.5691+00
23	2	3	2025-12-06 11:46:37.5691+00
24	2	4	2025-12-06 11:46:37.5691+00
25	2	5	2025-12-06 11:46:37.5691+00
26	2	10	2025-12-06 11:46:37.5691+00
27	2	11	2025-12-06 11:46:37.5691+00
28	2	12	2025-12-06 11:46:37.5691+00
29	2	13	2025-12-06 11:46:37.5691+00
30	2	20	2025-12-06 11:46:37.5691+00
31	2	21	2025-12-06 11:46:37.5691+00
32	2	22	2025-12-06 11:46:37.5691+00
33	2	23	2025-12-06 11:46:37.5691+00
34	2	30	2025-12-06 11:46:37.5691+00
35	2	31	2025-12-06 11:46:37.5691+00
36	2	32	2025-12-06 11:46:37.5691+00
37	2	33	2025-12-06 11:46:37.5691+00
38	2	34	2025-12-06 11:46:37.5691+00
39	2	40	2025-12-06 11:46:37.5691+00
40	2	41	2025-12-06 11:46:37.5691+00
41	2	42	2025-12-06 11:46:37.5691+00
42	3	1	2025-12-06 11:46:37.5691+00
43	3	20	2025-12-06 11:46:37.5691+00
44	3	23	2025-12-06 11:46:37.5691+00
45	3	30	2025-12-06 11:46:37.5691+00
46	3	40	2025-12-06 11:46:37.5691+00
47	3	41	2025-12-06 11:46:37.5691+00
48	4	10	2025-12-06 11:46:37.5691+00
49	4	11	2025-12-06 11:46:37.5691+00
50	4	12	2025-12-06 11:46:37.5691+00
51	4	20	2025-12-06 11:46:37.5691+00
52	4	21	2025-12-06 11:46:37.5691+00
53	4	22	2025-12-06 11:46:37.5691+00
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.roles (id, name, description, is_system_role, created_at, updated_at) FROM stdin;
1	owner	Chủ sở hữu hệ thống - Toàn quyền	t	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
2	admin	Quản trị viên - Quản lý hệ thống	t	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
3	staff	Nhân viên - Hỗ trợ khách hàng	t	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
4	customer	Khách hàng - Người dùng thông thường	t	2025-12-06 11:46:37.5691+00	2025-12-06 11:46:37.5691+00
\.


--
-- Data for Name: system_settings; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.system_settings (id, key, value, description, is_public, created_at, updated_at) FROM stdin;
1	registration_fields	{"fields": [{"key": "fullName", "type": "text", "label": "Họ và Tên", "enabled": true, "required": true, "placeholder": "Nhập họ và tên đầy đủ"}, {"key": "email", "type": "email", "label": "Email", "enabled": true, "required": true, "placeholder": "example@gmail.com"}, {"key": "phone", "type": "tel", "label": "Số Điện Thoại", "enabled": true, "required": true, "placeholder": "+84 xxx xxx xxx"}, {"key": "dateOfBirth", "type": "date", "label": "Ngày Sinh", "enabled": true, "required": false, "placeholder": ""}, {"key": "password", "type": "password", "label": "Mật Khẩu", "enabled": true, "required": true, "placeholder": "Tối thiểu 8 ký tự"}, {"key": "confirmPassword", "type": "password", "label": "Xác Nhận Mật Khẩu", "enabled": true, "required": true, "placeholder": "Nhập lại mật khẩu"}, {"key": "country", "type": "select", "label": "Quốc Gia", "enabled": true, "required": true, "placeholder": "Chọn quốc gia"}, {"key": "tradingExperience", "type": "select", "label": "Kinh Nghiệm Giao Dịch", "enabled": true, "required": false, "placeholder": "Chọn mức độ kinh nghiệm"}, {"key": "referralCode", "type": "text", "label": "Mã Giới Thiệu", "enabled": true, "required": false, "placeholder": "Nhập mã giới thiệu (nếu có)"}, {"key": "agreeTerms", "type": "checkbox", "label": "Đồng ý điều khoản", "enabled": true, "required": true, "placeholder": ""}, {"key": "agreeMarketing", "type": "checkbox", "label": "Đồng ý nhận marketing", "enabled": true, "required": false, "placeholder": ""}]}	Cấu hình các trường đăng ký người dùng	t	2025-12-06 22:18:33.131343+00	2025-12-06 22:18:33.131343+00
\.


--
-- Data for Name: trading_bots; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.trading_bots (id, user_id, name, description, strategy_id, strategy_name, strategy_parameters, symbols, base_amount, leverage, max_positions, risk_per_trade, status, last_run_at, next_run_at, total_trades, winning_trades, losing_trades, total_pnl, max_drawdown, logs, error_count, last_error, last_error_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: trading_orders; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.trading_orders (id, user_id, order_type, symbol, side, quantity, price, stop_price, time_in_force, status, filled_quantity, filled_price, remaining_quantity, average_price, commission, source, ip_address, user_agent, filled_at, cancelled_at, expires_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: trailing_stop_orders; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.trailing_stop_orders (id, user_id, parent_order_id, symbol, side, quantity, stop_type, stop_value, trailing_distance, current_stop_price, activation_price, highest_price, lowest_price, status, triggered_at, completed_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: transactions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.transactions (id, user_id, transaction_type, category, asset, amount, fee, net_amount, balance_before, balance_after, status, reference_id, external_id, description, bank_account, bank_name, transaction_hash, from_address, to_address, network, confirmations, metadata, ip_address, completed_at, cancelled_at, failed_reason, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: user_profiles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_profiles (id, user_id, full_name, display_name, date_of_birth, phone, address, country, city, postal_code, id_type, id_number, id_verified, id_front_url, id_back_url, selfie_url, bank_account_name, bank_account_number, bank_name, bank_branch, emergency_contact_name, emergency_contact_phone, preferences, notification_settings, avatar_url, created_at, updated_at) FROM stdin;
1	1	System Administrator	Admin	\N	\N	\N	\N	\N	\N	\N	\N	f	\N	\N	\N	\N	\N	\N	\N	\N	\N	{}	{"sms": false, "push": true, "email": true}	\N	2025-12-06 15:01:26.603385+00	2025-12-06 15:01:26.603385+00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, email, password_hash, role_id, status, email_verified, phone_verified, kyc_status, customer_payment_id, referral_code, referred_by, last_login_at, failed_login_attempts, account_locked_until, terms_accepted_at, privacy_accepted_at, created_at, updated_at) FROM stdin;
1	admin@digitalutopia.com	$pbkdf2-sha256$29000$gJBSyrlXKoUQQmgt5dx7rw$i2leow8TGLBjZdO7kTQjwxO1.UcjXcy56T/LcA5fhQI	2	active	t	f	verified	\N	\N	\N	2025-12-06 20:59:21.033587+00	0	\N	\N	\N	2025-12-06 15:01:26.537674+00	2025-12-06 20:59:20.999812+00
\.


--
-- Data for Name: wallet_balances; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.wallet_balances (id, user_id, asset, available_balance, locked_balance, pending_balance, reserved_balance, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: watchlists; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.watchlists (id, user_id, name, description, symbols, is_default, is_public, sort_order, created_at, updated_at) FROM stdin;
\.


--
-- Name: aml_screenings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.aml_screenings_id_seq', 1, false);


--
-- Name: analytics_events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.analytics_events_id_seq', 1, false);


--
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.audit_logs_id_seq', 19, true);


--
-- Name: compliance_events_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.compliance_events_id_seq', 1, false);


--
-- Name: exchange_rates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exchange_rates_id_seq', 6, true);


--
-- Name: iceberg_orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.iceberg_orders_id_seq', 1, false);


--
-- Name: kyc_documents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.kyc_documents_id_seq', 1, false);


--
-- Name: market_analysis_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.market_analysis_id_seq', 1, false);


--
-- Name: market_data_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.market_data_history_id_seq', 1, false);


--
-- Name: market_prices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.market_prices_id_seq', 1, false);


--
-- Name: oco_orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.oco_orders_id_seq', 1, false);


--
-- Name: permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.permissions_id_seq', 1, false);


--
-- Name: portfolio_positions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.portfolio_positions_id_seq', 1, false);


--
-- Name: referral_codes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.referral_codes_id_seq', 1, false);


--
-- Name: referral_registrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.referral_registrations_id_seq', 1, false);


--
-- Name: refresh_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.refresh_tokens_id_seq', 3, true);


--
-- Name: risk_assessments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.risk_assessments_id_seq', 1, false);


--
-- Name: role_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.role_permissions_id_seq', 53, true);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_id_seq', 1, false);


--
-- Name: system_settings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.system_settings_id_seq', 1, true);


--
-- Name: trading_bots_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.trading_bots_id_seq', 1, false);


--
-- Name: trading_orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.trading_orders_id_seq', 1, false);


--
-- Name: trailing_stop_orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.trailing_stop_orders_id_seq', 1, false);


--
-- Name: transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.transactions_id_seq', 1, false);


--
-- Name: user_profiles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_profiles_id_seq', 1, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: wallet_balances_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.wallet_balances_id_seq', 1, false);


--
-- Name: watchlists_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.watchlists_id_seq', 1, false);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: aml_screenings aml_screenings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.aml_screenings
    ADD CONSTRAINT aml_screenings_pkey PRIMARY KEY (id);


--
-- Name: analytics_events analytics_events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analytics_events
    ADD CONSTRAINT analytics_events_pkey PRIMARY KEY (id);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: compliance_events compliance_events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compliance_events
    ADD CONSTRAINT compliance_events_pkey PRIMARY KEY (id);


--
-- Name: exchange_rates exchange_rates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exchange_rates
    ADD CONSTRAINT exchange_rates_pkey PRIMARY KEY (id);


--
-- Name: iceberg_orders iceberg_orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.iceberg_orders
    ADD CONSTRAINT iceberg_orders_pkey PRIMARY KEY (id);


--
-- Name: kyc_documents kyc_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kyc_documents
    ADD CONSTRAINT kyc_documents_pkey PRIMARY KEY (id);


--
-- Name: market_analysis market_analysis_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.market_analysis
    ADD CONSTRAINT market_analysis_pkey PRIMARY KEY (id);


--
-- Name: market_data_history market_data_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.market_data_history
    ADD CONSTRAINT market_data_history_pkey PRIMARY KEY (id);


--
-- Name: market_prices market_prices_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.market_prices
    ADD CONSTRAINT market_prices_pkey PRIMARY KEY (id);


--
-- Name: market_prices market_prices_symbol_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.market_prices
    ADD CONSTRAINT market_prices_symbol_key UNIQUE (symbol);


--
-- Name: oco_orders oco_orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.oco_orders
    ADD CONSTRAINT oco_orders_pkey PRIMARY KEY (id);


--
-- Name: permissions permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (id);


--
-- Name: portfolio_positions portfolio_positions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.portfolio_positions
    ADD CONSTRAINT portfolio_positions_pkey PRIMARY KEY (id);


--
-- Name: referral_codes referral_codes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.referral_codes
    ADD CONSTRAINT referral_codes_pkey PRIMARY KEY (id);


--
-- Name: referral_registrations referral_registrations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.referral_registrations
    ADD CONSTRAINT referral_registrations_pkey PRIMARY KEY (id);


--
-- Name: referral_registrations referral_registrations_referred_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.referral_registrations
    ADD CONSTRAINT referral_registrations_referred_user_id_key UNIQUE (referred_user_id);


--
-- Name: refresh_tokens refresh_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_pkey PRIMARY KEY (id);


--
-- Name: refresh_tokens refresh_tokens_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_token_key UNIQUE (token);


--
-- Name: risk_assessments risk_assessments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.risk_assessments
    ADD CONSTRAINT risk_assessments_pkey PRIMARY KEY (id);


--
-- Name: role_permissions role_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_pkey PRIMARY KEY (id);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: system_settings system_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_settings
    ADD CONSTRAINT system_settings_pkey PRIMARY KEY (id);


--
-- Name: trading_bots trading_bots_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trading_bots
    ADD CONSTRAINT trading_bots_pkey PRIMARY KEY (id);


--
-- Name: trading_orders trading_orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trading_orders
    ADD CONSTRAINT trading_orders_pkey PRIMARY KEY (id);


--
-- Name: trailing_stop_orders trailing_stop_orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trailing_stop_orders
    ADD CONSTRAINT trailing_stop_orders_pkey PRIMARY KEY (id);


--
-- Name: transactions transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_pkey PRIMARY KEY (id);


--
-- Name: exchange_rates uq_exchange_rate_pair; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exchange_rates
    ADD CONSTRAINT uq_exchange_rate_pair UNIQUE (base_asset, target_asset);


--
-- Name: wallet_balances uq_wallet_user_asset; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.wallet_balances
    ADD CONSTRAINT uq_wallet_user_asset UNIQUE (user_id, asset);


--
-- Name: user_profiles user_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_profiles
    ADD CONSTRAINT user_profiles_pkey PRIMARY KEY (id);


--
-- Name: user_profiles user_profiles_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_profiles
    ADD CONSTRAINT user_profiles_user_id_key UNIQUE (user_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: wallet_balances wallet_balances_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.wallet_balances
    ADD CONSTRAINT wallet_balances_pkey PRIMARY KEY (id);


--
-- Name: watchlists watchlists_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.watchlists
    ADD CONSTRAINT watchlists_pkey PRIMARY KEY (id);


--
-- Name: idx_market_data_symbol_timeframe_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_market_data_symbol_timeframe_timestamp ON public.market_data_history USING btree (symbol, timeframe, "timestamp");


--
-- Name: ix_aml_screenings_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_aml_screenings_id ON public.aml_screenings USING btree (id);


--
-- Name: ix_aml_screenings_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_aml_screenings_status ON public.aml_screenings USING btree (status);


--
-- Name: ix_aml_screenings_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_aml_screenings_user_id ON public.aml_screenings USING btree (user_id);


--
-- Name: ix_analytics_events_event_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_analytics_events_event_category ON public.analytics_events USING btree (event_category);


--
-- Name: ix_analytics_events_event_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_analytics_events_event_name ON public.analytics_events USING btree (event_name);


--
-- Name: ix_analytics_events_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_analytics_events_id ON public.analytics_events USING btree (id);


--
-- Name: ix_analytics_events_session_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_analytics_events_session_id ON public.analytics_events USING btree (session_id);


--
-- Name: ix_analytics_events_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_analytics_events_user_id ON public.analytics_events USING btree (user_id);


--
-- Name: ix_audit_logs_action; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_action ON public.audit_logs USING btree (action);


--
-- Name: ix_audit_logs_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_created_at ON public.audit_logs USING btree (created_at);


--
-- Name: ix_audit_logs_resource_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_resource_id ON public.audit_logs USING btree (resource_id);


--
-- Name: ix_audit_logs_resource_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_resource_type ON public.audit_logs USING btree (resource_type);


--
-- Name: ix_audit_logs_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_user_id ON public.audit_logs USING btree (user_id);


--
-- Name: ix_compliance_events_event_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_compliance_events_event_type ON public.compliance_events USING btree (event_type);


--
-- Name: ix_compliance_events_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_compliance_events_id ON public.compliance_events USING btree (id);


--
-- Name: ix_compliance_events_severity; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_compliance_events_severity ON public.compliance_events USING btree (severity);


--
-- Name: ix_compliance_events_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_compliance_events_status ON public.compliance_events USING btree (status);


--
-- Name: ix_compliance_events_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_compliance_events_user_id ON public.compliance_events USING btree (user_id);


--
-- Name: ix_exchange_rates_base_asset; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_exchange_rates_base_asset ON public.exchange_rates USING btree (base_asset);


--
-- Name: ix_exchange_rates_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_exchange_rates_id ON public.exchange_rates USING btree (id);


--
-- Name: ix_exchange_rates_target_asset; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_exchange_rates_target_asset ON public.exchange_rates USING btree (target_asset);


--
-- Name: ix_iceberg_orders_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_iceberg_orders_id ON public.iceberg_orders USING btree (id);


--
-- Name: ix_iceberg_orders_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_iceberg_orders_status ON public.iceberg_orders USING btree (status);


--
-- Name: ix_iceberg_orders_symbol; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_iceberg_orders_symbol ON public.iceberg_orders USING btree (symbol);


--
-- Name: ix_kyc_documents_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_kyc_documents_id ON public.kyc_documents USING btree (id);


--
-- Name: ix_kyc_documents_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_kyc_documents_user_id ON public.kyc_documents USING btree (user_id);


--
-- Name: ix_kyc_documents_verification_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_kyc_documents_verification_status ON public.kyc_documents USING btree (verification_status);


--
-- Name: ix_market_analysis_analysis_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_market_analysis_analysis_date ON public.market_analysis USING btree (analysis_date);


--
-- Name: ix_market_analysis_analysis_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_market_analysis_analysis_type ON public.market_analysis USING btree (analysis_type);


--
-- Name: ix_market_analysis_symbol; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_market_analysis_symbol ON public.market_analysis USING btree (symbol);


--
-- Name: ix_market_data_history_symbol; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_market_data_history_symbol ON public.market_data_history USING btree (symbol);


--
-- Name: ix_market_data_history_timeframe; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_market_data_history_timeframe ON public.market_data_history USING btree (timeframe);


--
-- Name: ix_market_data_history_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_market_data_history_timestamp ON public.market_data_history USING btree ("timestamp");


--
-- Name: ix_market_prices_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_market_prices_is_active ON public.market_prices USING btree (is_active);


--
-- Name: ix_market_prices_last_update; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_market_prices_last_update ON public.market_prices USING btree (last_update);


--
-- Name: ix_market_prices_symbol; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_market_prices_symbol ON public.market_prices USING btree (symbol);


--
-- Name: ix_oco_orders_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_oco_orders_id ON public.oco_orders USING btree (id);


--
-- Name: ix_oco_orders_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_oco_orders_status ON public.oco_orders USING btree (status);


--
-- Name: ix_oco_orders_symbol; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_oco_orders_symbol ON public.oco_orders USING btree (symbol);


--
-- Name: ix_permissions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_permissions_id ON public.permissions USING btree (id);


--
-- Name: ix_permissions_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_permissions_name ON public.permissions USING btree (name);


--
-- Name: ix_portfolio_positions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_portfolio_positions_id ON public.portfolio_positions USING btree (id);


--
-- Name: ix_portfolio_positions_is_closed; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_portfolio_positions_is_closed ON public.portfolio_positions USING btree (is_closed);


--
-- Name: ix_portfolio_positions_symbol; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_portfolio_positions_symbol ON public.portfolio_positions USING btree (symbol);


--
-- Name: ix_portfolio_positions_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_portfolio_positions_user_id ON public.portfolio_positions USING btree (user_id);


--
-- Name: ix_referral_codes_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_referral_codes_code ON public.referral_codes USING btree (code);


--
-- Name: ix_referral_codes_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_referral_codes_id ON public.referral_codes USING btree (id);


--
-- Name: ix_referral_codes_staff_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_referral_codes_staff_id ON public.referral_codes USING btree (staff_id);


--
-- Name: ix_referral_codes_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_referral_codes_status ON public.referral_codes USING btree (status);


--
-- Name: ix_referral_codes_token; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_referral_codes_token ON public.referral_codes USING btree (token);


--
-- Name: ix_referral_registrations_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_referral_registrations_id ON public.referral_registrations USING btree (id);


--
-- Name: ix_referral_registrations_referral_code_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_referral_registrations_referral_code_id ON public.referral_registrations USING btree (referral_code_id);


--
-- Name: ix_referral_registrations_referred_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_referral_registrations_referred_user_id ON public.referral_registrations USING btree (referred_user_id);


--
-- Name: ix_refresh_tokens_expires_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_refresh_tokens_expires_at ON public.refresh_tokens USING btree (expires_at);


--
-- Name: ix_refresh_tokens_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_refresh_tokens_id ON public.refresh_tokens USING btree (id);


--
-- Name: ix_refresh_tokens_revoked; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_refresh_tokens_revoked ON public.refresh_tokens USING btree (revoked);


--
-- Name: ix_refresh_tokens_token; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_refresh_tokens_token ON public.refresh_tokens USING btree (token);


--
-- Name: ix_refresh_tokens_token_hash; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_refresh_tokens_token_hash ON public.refresh_tokens USING btree (token_hash);


--
-- Name: ix_refresh_tokens_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_refresh_tokens_user_id ON public.refresh_tokens USING btree (user_id);


--
-- Name: ix_risk_assessments_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_risk_assessments_id ON public.risk_assessments USING btree (id);


--
-- Name: ix_risk_assessments_risk_level; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_risk_assessments_risk_level ON public.risk_assessments USING btree (risk_level);


--
-- Name: ix_risk_assessments_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_risk_assessments_status ON public.risk_assessments USING btree (status);


--
-- Name: ix_risk_assessments_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_risk_assessments_user_id ON public.risk_assessments USING btree (user_id);


--
-- Name: ix_role_permissions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_role_permissions_id ON public.role_permissions USING btree (id);


--
-- Name: ix_roles_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_roles_id ON public.roles USING btree (id);


--
-- Name: ix_roles_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_roles_name ON public.roles USING btree (name);


--
-- Name: ix_system_settings_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_system_settings_id ON public.system_settings USING btree (id);


--
-- Name: ix_system_settings_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_system_settings_key ON public.system_settings USING btree (key);


--
-- Name: ix_trading_bots_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_trading_bots_id ON public.trading_bots USING btree (id);


--
-- Name: ix_trading_bots_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_trading_bots_status ON public.trading_bots USING btree (status);


--
-- Name: ix_trading_bots_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_trading_bots_user_id ON public.trading_bots USING btree (user_id);


--
-- Name: ix_trading_orders_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_trading_orders_id ON public.trading_orders USING btree (id);


--
-- Name: ix_trading_orders_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_trading_orders_status ON public.trading_orders USING btree (status);


--
-- Name: ix_trading_orders_symbol; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_trading_orders_symbol ON public.trading_orders USING btree (symbol);


--
-- Name: ix_trading_orders_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_trading_orders_user_id ON public.trading_orders USING btree (user_id);


--
-- Name: ix_trailing_stop_orders_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_trailing_stop_orders_id ON public.trailing_stop_orders USING btree (id);


--
-- Name: ix_trailing_stop_orders_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_trailing_stop_orders_status ON public.trailing_stop_orders USING btree (status);


--
-- Name: ix_trailing_stop_orders_symbol; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_trailing_stop_orders_symbol ON public.trailing_stop_orders USING btree (symbol);


--
-- Name: ix_transactions_asset; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_transactions_asset ON public.transactions USING btree (asset);


--
-- Name: ix_transactions_external_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_transactions_external_id ON public.transactions USING btree (external_id);


--
-- Name: ix_transactions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_transactions_id ON public.transactions USING btree (id);


--
-- Name: ix_transactions_reference_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_transactions_reference_id ON public.transactions USING btree (reference_id);


--
-- Name: ix_transactions_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_transactions_status ON public.transactions USING btree (status);


--
-- Name: ix_transactions_transaction_hash; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_transactions_transaction_hash ON public.transactions USING btree (transaction_hash);


--
-- Name: ix_transactions_transaction_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_transactions_transaction_type ON public.transactions USING btree (transaction_type);


--
-- Name: ix_transactions_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_transactions_user_id ON public.transactions USING btree (user_id);


--
-- Name: ix_user_profiles_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_profiles_id ON public.user_profiles USING btree (id);


--
-- Name: ix_user_profiles_phone; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_profiles_phone ON public.user_profiles USING btree (phone);


--
-- Name: ix_users_customer_payment_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_customer_payment_id ON public.users USING btree (customer_payment_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_kyc_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_kyc_status ON public.users USING btree (kyc_status);


--
-- Name: ix_users_referral_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_referral_code ON public.users USING btree (referral_code);


--
-- Name: ix_users_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_status ON public.users USING btree (status);


--
-- Name: ix_wallet_balances_asset; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_wallet_balances_asset ON public.wallet_balances USING btree (asset);


--
-- Name: ix_wallet_balances_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_wallet_balances_id ON public.wallet_balances USING btree (id);


--
-- Name: ix_wallet_balances_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_wallet_balances_user_id ON public.wallet_balances USING btree (user_id);


--
-- Name: ix_watchlists_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_watchlists_id ON public.watchlists USING btree (id);


--
-- Name: aml_screenings aml_screenings_reviewed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.aml_screenings
    ADD CONSTRAINT aml_screenings_reviewed_by_fkey FOREIGN KEY (reviewed_by) REFERENCES public.users(id);


--
-- Name: aml_screenings aml_screenings_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.aml_screenings
    ADD CONSTRAINT aml_screenings_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: analytics_events analytics_events_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.analytics_events
    ADD CONSTRAINT analytics_events_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: audit_logs audit_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: compliance_events compliance_events_assigned_to_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compliance_events
    ADD CONSTRAINT compliance_events_assigned_to_fkey FOREIGN KEY (assigned_to) REFERENCES public.users(id);


--
-- Name: compliance_events compliance_events_escalated_to_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compliance_events
    ADD CONSTRAINT compliance_events_escalated_to_fkey FOREIGN KEY (escalated_to) REFERENCES public.users(id);


--
-- Name: compliance_events compliance_events_resolved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compliance_events
    ADD CONSTRAINT compliance_events_resolved_by_fkey FOREIGN KEY (resolved_by) REFERENCES public.users(id);


--
-- Name: compliance_events compliance_events_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.compliance_events
    ADD CONSTRAINT compliance_events_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: iceberg_orders iceberg_orders_parent_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.iceberg_orders
    ADD CONSTRAINT iceberg_orders_parent_order_id_fkey FOREIGN KEY (parent_order_id) REFERENCES public.trading_orders(id);


--
-- Name: iceberg_orders iceberg_orders_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.iceberg_orders
    ADD CONSTRAINT iceberg_orders_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: kyc_documents kyc_documents_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kyc_documents
    ADD CONSTRAINT kyc_documents_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: kyc_documents kyc_documents_verified_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kyc_documents
    ADD CONSTRAINT kyc_documents_verified_by_fkey FOREIGN KEY (verified_by) REFERENCES public.users(id);


--
-- Name: oco_orders oco_orders_primary_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.oco_orders
    ADD CONSTRAINT oco_orders_primary_order_id_fkey FOREIGN KEY (primary_order_id) REFERENCES public.trading_orders(id);


--
-- Name: oco_orders oco_orders_secondary_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.oco_orders
    ADD CONSTRAINT oco_orders_secondary_order_id_fkey FOREIGN KEY (secondary_order_id) REFERENCES public.trading_orders(id);


--
-- Name: oco_orders oco_orders_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.oco_orders
    ADD CONSTRAINT oco_orders_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: portfolio_positions portfolio_positions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.portfolio_positions
    ADD CONSTRAINT portfolio_positions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: referral_codes referral_codes_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.referral_codes
    ADD CONSTRAINT referral_codes_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: referral_codes referral_codes_staff_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.referral_codes
    ADD CONSTRAINT referral_codes_staff_id_fkey FOREIGN KEY (staff_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: referral_registrations referral_registrations_referral_code_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.referral_registrations
    ADD CONSTRAINT referral_registrations_referral_code_id_fkey FOREIGN KEY (referral_code_id) REFERENCES public.referral_codes(id);


--
-- Name: referral_registrations referral_registrations_referred_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.referral_registrations
    ADD CONSTRAINT referral_registrations_referred_user_id_fkey FOREIGN KEY (referred_user_id) REFERENCES public.users(id);


--
-- Name: refresh_tokens refresh_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: risk_assessments risk_assessments_assessed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.risk_assessments
    ADD CONSTRAINT risk_assessments_assessed_by_fkey FOREIGN KEY (assessed_by) REFERENCES public.users(id);


--
-- Name: risk_assessments risk_assessments_previous_assessment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.risk_assessments
    ADD CONSTRAINT risk_assessments_previous_assessment_id_fkey FOREIGN KEY (previous_assessment_id) REFERENCES public.risk_assessments(id);


--
-- Name: risk_assessments risk_assessments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.risk_assessments
    ADD CONSTRAINT risk_assessments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: role_permissions role_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permissions(id) ON DELETE CASCADE;


--
-- Name: role_permissions role_permissions_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- Name: trading_bots trading_bots_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trading_bots
    ADD CONSTRAINT trading_bots_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: trading_orders trading_orders_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trading_orders
    ADD CONSTRAINT trading_orders_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: trailing_stop_orders trailing_stop_orders_parent_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trailing_stop_orders
    ADD CONSTRAINT trailing_stop_orders_parent_order_id_fkey FOREIGN KEY (parent_order_id) REFERENCES public.trading_orders(id);


--
-- Name: trailing_stop_orders trailing_stop_orders_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trailing_stop_orders
    ADD CONSTRAINT trailing_stop_orders_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: transactions transactions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_profiles user_profiles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_profiles
    ADD CONSTRAINT user_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: users users_referred_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_referred_by_fkey FOREIGN KEY (referred_by) REFERENCES public.users(id);


--
-- Name: users users_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id);


--
-- Name: wallet_balances wallet_balances_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.wallet_balances
    ADD CONSTRAINT wallet_balances_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: watchlists watchlists_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.watchlists
    ADD CONSTRAINT watchlists_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict GeNZflRIBa8FWiCmu8SqfRbabctay8tBxW4UbPFNXp9XspZRH4JE2kEciEtiDX3

