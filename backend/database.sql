pragma foregin_keys = on;

CREATE TABLE vessels (
    mmsi                integer UNIQUE NOT NULL primary key,
    vessel_name         varchar,
    callsign            varchar,
    timestamp           varchar,
    heading             float NOT NULL, -- bearing
    speed               float NOT NULL, --kts
    current_status      varchar DEFAULT 'anchored',
    -- voyage              varchar, -- array of port.ids?
    src                 varchar, -- not sure if I want this to be source.id, or if I want data such as "AIS".
    type                varchar DEFAULT 'OTHER' check (type in ( 'OTHER', 'CARGO', 'FISHING', 'TUG', 'TANKER', 'RECREATIONAL', 'PUBLIC')),
    flag                varchar DEFAULT 'OTHER',
    length              float NOT NULL,
    width               float NOT NULL,
    draft               float NOT NULL,
    cargo_weight        float NOT NULL,
    geom                geometry, -- Point
    -- Use these for geom?
    lat                 float NOT NULL,
    lon                 float NOT NULL,
    dist_from_shore     float, --km
    dist_from_port      float --km
);

CREATE TABLE mock_ships (
    mmsi             int UNIQUE NOT NULL primary key,
    geom             geometry, -- Point
    lat              int NOT NULL,
    lon              int NOT NULL,
    heading          int NOT NULL,
    speed            float, --units?
    current_status   varchar DEFAULT 'anchored',
    src              int NOT NULL, -- REFERENCES users(id),
    type             varchar DEFAULT 'OTHER' check (type in ( 'OTHER', 'CARGO', 'FISHING', 'TUG', 'TANKER', 'RECREATIONAL', 'PASSENGER')),
    flag             varchar DEFAULT 'OTHER',
    length           float NOT NULL,
    width            float NOT NULL,
    draft            float NOT NULL,
    cargo_weight     float NOT NULL,
    -- Maybe calculate from lat,lon decided by users
    dist_from_shore  float,
    dist_from_port   float
);

CREATE TABLE sources (
    id          varchar UNIQUE NOT NULL primary key,
    name        varchar, -- GFW, MarineCadastre, Copernicus, COOP and Weather API (stations/regions), NCEI
    -- API         varchar,
    -- datums      varchar, -- "DATUM1 DATUM2 DATUM3 DATUM4 ... DATUMn"
    region      varchar, -- Operational jurisdiction of source (If database, note "database")
    timeZone    varchar,
    geom        geometry, -- Polygon
    type        varchar
);

CREATE TABLE zones (
    id varchar UNIQUE NOT NULL primary key,
    geom geometry NOT NULL, -- Polygon
    src_id varchar NOT NULL, -- REFERENCES sources(id),
    region varchar, -- US-IA
    -- "High Seas" option can just be inverse of EEZ regions
    type varchar check (type in ('MET', 'MARINE', 'EEZ', 'PROTECTED', 'RESTRICTED-FISH'))
);

CREATE TABLE ports (
    id          integer UNIQUE NOT NULL primary key,
    name        varchar, -- reported Port ID, callsign (Like Airport ISO code?)?
    nationality varchar, -- Akin to region?
    lat         int NOT NULL,
    lon         int NOT NULL,
    geom        geometry -- Polygon for jurisdiction?, Point for physical location?
);

CREATE TABLE meteorology (
    -- Would it be better to specify each type as an attr or as its own entity denoting type?
    id              integer UNIQUE NOT NULL primary key,
    src_id          varchar, -- REFERENCES sources(id),
    lat             int,
    long            int,
    -- type varchar, -- Temp, humidity, wind speed, percipitation, etc.
    -- data varchar, -- data reported by source
    temp            float,
    humidity        float,
    wind_speed      float,
    wind_heading    float,
    percipitation   boolean,
    forecast        int[], -- array of other id's referencing this table. Forecasts entered as entities, and then updated if they match src_id, lat, lon, type, and timestamp?
    timestamp       int,
    geom            geometry, -- Polygon, or Point based off lat,lon values?
    event_id        int, --REFERENCES events(id), -- if NULL, ignore
    region          varchar -- REFERENCES sources(region)
);

CREATE TABLE oceanography (
    id              integer UNIQUE NOT NULL primary key,
    src_id          varchar, -- REFERENCES sources(id),
    lat             int,
    long            int,
    -- type varchar, -- wave height, water temp, "water physics"
    -- data varchar, -- data reported by source
    wave_height     float,
    water_temp      float,
    water_physics   varchar, -- what?
    timestamp       int,
    geom            geometry, -- Polygon
    region          varchar, -- REFERENCES sources(region),
    event_id        int -- REFERENCES events(id) -- if NULL, ignore
);

CREATE TABLE events (
    id          integer UNIQUE NOT NULL primary key,
    src_id      varchar, -- REFERENCES sources(id),
    region      varchar, -- REFERENCES sources(region),
    timestamp   int, -- timestamp event was reported to DB
    begin_time  int,
    end_time    int,
    active      boolean NOT NULL, -- Wonder if I can calulate this based off reported timestamp
    -- Would it be worth it to DELETE from DB automatically?
    type        varchar, -- Storm, geopolitical, shipping notice, oceanographic, etc.
    description varchar
);

CREATE TABLE users (
    id          int UNIQUE NOT NULL primary key,
    uhash       varchar UNIQUE NOT NULL,
    phash       varchar NOT NULL,
    first_name  varchar,
    last_name   varchar,
    email       varchar UNIQUE NOT NULL,
    last_logon  varchar NOT NULL DEFAULT 0,
    mfa         boolean NOT NULL DEFAULT false,
    countdown   int NOT NULL DEFAULT 90 CHECK (countdown > 0), -- set to 90 days?
    reg_date    varchar DEFAULT current_date,
    -- ALWAYS pull existing IDs when users login confirmed
    -- How to assign array datatype?
    presets     int[10] -- REFERENCES preset(id) -- array of preset.id to ensure order of presets pulled
);

CREATE TABLE presets (
    id          int NOT NULL UNIQUE primary key,
    users_id     int NOT NULL, -- REFERENCES users(id), -- group by and then pull all presets assigned to users
    geom        geometry,
    filters     varchar -- "FILTER1 FILTER 2 FILTER3 FILTER4 ... FILTERn"
);

