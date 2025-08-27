--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5 (Debian 17.5-1.pgdg120+1)
-- Dumped by pg_dump version 17.5 (Ubuntu 17.5-1.pgdg22.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: vanna; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA vanna;


ALTER SCHEMA vanna OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: mahasiswa; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mahasiswa (
    nim character varying(16) NOT NULL,
    nama character varying(128), 
    tempat_lahir character varying(64), 
    tgl_lahir timestamp(0) without time zone,
    jalur character varying(64),
    penerimaan character varying(100),
    alamat character varying(256),
    fakultas character varying(64),
    prodi character varying(256),
    status character varying(2),
    sumber_biaya character varying(20), 
    status_mahasiswa character varying(64), 
    angkatan numeric(38,0) NOT NULL, 
    jenis_kelamin character(1),
    jenjang character varying(20),
    asal_kota character varying(64),
    asal_provinsi character varying(64),
    asal_negara character varying(512),
    kewarganegaraan character varying(20),
    penghasilan_ortu bigint,
    kebangsaan character varying(512),
    agama character varying(32),
    kelompok_biaya character varying(256),
    bidikmisi character varying(5) 
);


ALTER TABLE public.mahasiswa OWNER TO postgres;

--
-- Name: prestasi_mawa; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.prestasi_mawa (
    nim_mhs character varying(16),
    nm_pengguna character varying(128),
    nm_jenjang character varying(20),
    nm_program_studi character varying(256),
    nm_fakultas character varying(64),
    nm_krp_khp character varying(5000),
    tahun_krp_khp numeric,
    tahun_ajaran character varying(12),
    nm_semester character varying(64),
    nm_jabatan_prestasi character varying(64),
    nm_tingkat character varying(32),
    nm_kegiatan_1 character varying(512),
    nm_kelompok_kegiatan character varying(64),
    waktu_krp_khp character varying(256),
    nidn_dosen character varying(24),
    nip_dosen character varying(24),
    pembimbing_nama character varying(255),
    jenjang_prodi_dosen character varying(20),
    prodi_dosen character varying(256),
    fakultas_dosen character varying(64),
    id_program_studi character varying(255),
    id_fakultas character varying(255),
    penyelenggara_krp_khp character varying(255)
);


ALTER TABLE public.prestasi_mawa OWNER TO postgres;

--
-- Name: v_mahasiswa; Type: VIEW; Schema: vanna; Owner: postgres
--

CREATE VIEW vanna.v_mahasiswa AS
 SELECT nim,
    nama,
    tempat_lahir,
    tgl_lahir,
    jalur,
    penerimaan,
    alamat,
    fakultas,
    prodi,
    status,
    sumber_biaya,
    status_mahasiswa,
    angkatan,
    jenis_kelamin,
    jenjang,
    asal_kota,
    asal_provinsi,
    asal_negara,
    kewarganegaraan,
    penghasilan_ortu,
    kebangsaan,
    agama,
    kelompok_biaya,
    bidikmisi
   FROM public.mahasiswa;


ALTER VIEW vanna.v_mahasiswa OWNER TO postgres;

--
-- Name: v_prestasi_mawa; Type: VIEW; Schema: vanna; Owner: postgres
--

CREATE VIEW vanna.v_prestasi_mawa AS
 SELECT nim_mhs,
    nm_pengguna,
    nm_jenjang,
    nm_program_studi,
    nm_fakultas,
    nm_krp_khp,
    tahun_krp_khp,
    tahun_ajaran,
    nm_semester,
    nm_jabatan_prestasi,
    nm_tingkat,
    nm_kegiatan_1,
    nm_kelompok_kegiatan,
    waktu_krp_khp,
    nidn_dosen,
    nip_dosen,
    pembimbing_nama,
    jenjang_prodi_dosen,
    prodi_dosen,
    fakultas_dosen,
    id_program_studi,
    id_fakultas,
    penyelenggara_krp_khp
   FROM public.prestasi_mawa;


ALTER VIEW vanna.v_prestasi_mawa OWNER TO postgres;

--
-- PostgreSQL database dump complete
--


-- Table to store information about academic staff
CREATE TABLE public.faculty (
    faculty_id INT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    department VARCHAR(100),
    title VARCHAR(100),
    hire_date DATE
);

ALTER TABLE public.faculty OWNER TO postgres;

-- Table to store information about research publications
CREATE TABLE public.publications (
    publication_id INT PRIMARY KEY,
    title TEXT NOT NULL,
    author_id INT,
    journal_name VARCHAR(255),
    publication_year INT,
    citation_count INT,
    FOREIGN KEY (author_id) REFERENCES public.faculty(faculty_id)
);

ALTER TABLE public.publications OWNER TO postgres;