ddl_statements = [
    """
CREATE VIEW vanna.v_mahasiswa AS
 SELECT 
    nim AS character varying(16) NOT NULL,
    nama AS character varying(128),
    tempat_lahir AS character varying(64),
    tgl_lahir AS timestamp(0) without time zone,
    jalur AS character varying(64),
    penerimaan AS character varying(100),
    alamat AS character varying(256),
    fakultas AS character varying(64),
    prodi AS character varying(256),
    status AS character varying(2),
    sumber_biaya AS character varying(20),
    status_mahasiswa AS character varying(64),
    angkatan AS numeric(38,0) NOT NULL,
    jenis_kelamin AS character(1),
    jenjang AS character varying(20),
    asal_kota AS character varying(64),
    asal_provinsi AS character varying(64),
    asal_negara AS character varying(512),
    kewarganegaraan AS character varying(20),
    penghasilan_ortu AS bigint,
    kebangsaan AS character varying(512),
    agama AS character varying(32),
    kelompok_biaya AS character varying(256),
    bidikmisi AS character varying(5)
   FROM mahasiswa;
-- View of students
""",
    """
CREATE VIEW vanna.v_prestasi_mawa AS
 SELECT 
    nim_mhs AS character varying(16),
    nm_pengguna AS character varying(128),
    nm_jenjang AS character varying(20),
    nm_program_studi AS character varying(256),
    nm_fakultas AS character varying(64),
    nm_krp_khp AS character varying(5000),
    tahun_krp_khp AS numeric,
    tahun_ajaran AS character varying(12),
    nm_semester AS character varying(64),
    nm_jabatan_prestasi AS character varying(64),
    nm_tingkat AS character varying(32),
    nm_kegiatan_1 AS character varying(512),
    nm_kelompok_kegiatan AS character varying(64),
    waktu_krp_khp AS character varying(256),
    nidn_dosen AS character varying(24),
    nip_dosen AS character varying(24),
    pembimbing_nama AS character varying(255),
    jenjang_prodi_dosen AS character varying(20),
    prodi_dosen AS character varying(256),
    fakultas_dosen AS character varying(64),
    id_program_studi AS character varying(255),
    id_fakultas AS character varying(255),
    penyelenggara_krp_khp AS character varying(255)
   FROM prestasi_mawa;
-- View of student achievements
""",
]
