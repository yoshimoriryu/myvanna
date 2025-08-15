training_pairs = [
    {
        "question": "Berapa jumlah mahasiswa yang terdaftar?",
        "sql": "SELECT COUNT(*) AS total_mahasiswa FROM vanna.v_mahasiswa WHERE nim IS NOT NULL;",
    },
    {
        "question": "Siapa mahasiswa dengan penghasilan orang tua tertinggi?",
        "sql": "SELECT nim, nama, penghasilan_ortu FROM vanna.v_mahasiswa WHERE penghasilan_ortu IS NOT NULL ORDER BY penghasilan_ortu DESC LIMIT 1;",
    },
    {
        "question": "Berapa jumlah mahasiswa per fakultas?",
        "sql": "SELECT fakultas, COUNT(*) AS jumlah_mahasiswa FROM vanna.v_mahasiswa WHERE fakultas IS NOT NULL GROUP BY fakultas ORDER BY jumlah_mahasiswa DESC;",
    },
    {
        "question": "Berapa jumlah mahasiswa per program studi?",
        "sql": "SELECT prodi, COUNT(*) AS jumlah_mahasiswa FROM vanna.v_mahasiswa WHERE prodi IS NOT NULL GROUP BY prodi ORDER BY jumlah_mahasiswa DESC;",
    },
    {
        "question": "Daftar mahasiswa yang menerima bidikmisi",
        "sql": "SELECT nim, nama, bidikmisi FROM vanna.v_mahasiswa WHERE bidikmisi = 'IYA' AND nim IS NOT NULL;",
    },
    {
        "question": "Berapa jumlah prestasi yang diraih mahasiswa setiap tahun?",
        "sql": "SELECT tahun_krp_khp, COUNT(*) AS jumlah_prestasi FROM vanna.v_prestasi_mawa WHERE tahun_krp_khp IS NOT NULL GROUP BY tahun_krp_khp ORDER BY tahun_krp_khp DESC;",
    },
    {
        "question": "Daftar mahasiswa dengan prestasi tingkat nasional",
        "sql": "SELECT nim_mhs, nm_pengguna, nm_jabatan_prestasi, nm_tingkat FROM vanna.v_prestasi_mawa WHERE nm_tingkat = 'Nasional' AND nim_mhs IS NOT NULL;",
    },
    {
        "question": "Berapa jumlah mahasiswa per angkatan?",
        "sql": "SELECT angkatan, COUNT(*) AS jumlah_mahasiswa FROM vanna.v_mahasiswa WHERE angkatan IS NOT NULL GROUP BY angkatan ORDER BY angkatan DESC;",
    },
    {
        "question": "Daftar mahasiswa berdasarkan agama",
        "sql": "SELECT agama, COUNT(*) AS jumlah_mahasiswa FROM vanna.v_mahasiswa WHERE agama IS NOT NULL GROUP BY agama ORDER BY jumlah_mahasiswa DESC;",
    },
    {
        "question": "Daftar prestasi mahasiswa beserta pembimbingnya",
        "sql": "SELECT nim_mhs, nm_pengguna, nm_jabatan_prestasi, pembimbing_nama FROM vanna.v_prestasi_mawa WHERE pembimbing_nama IS NOT NULL AND nim_mhs IS NOT NULL;",
    },
]
