import psycopg2
import psycopg2.extras
from faker import Faker
import random
import time
import datetime

# --- IMPORTANT: UPDATE YOUR DATABASE CONNECTION DETAILS HERE ---
DB_CONFIG = {
    "dbname": "chatbot",
    "user": "postgres",
    "password": "password",
    "host": "private-data-db",
    "port": "5432"
}

# --- SCRIPT CONFIGURATION ---
NUM_MAHASISWA = 100000
NUM_FACULTY = 500
NUM_PUBLICATIONS_PER_FACULTY = (1, 5) # Range of publications per faculty member
PRESTASI_RATIO = 0.2 # 20% of students will have achievements

# Initialize Faker for Indonesian data
fake = Faker('id_ID')

# --- Sample Data Definitions ---
FAKULTAS_PRODI = {
    "Fakultas Ilmu Komputer": ["Ilmu Komputer", "Sistem Informasi", "Teknologi Informasi"],
    "Fakultas Teknik": ["Teknik Elektro", "Teknik Mesin", "Teknik Sipil", "Teknik Industri"],
    "Fakultas Ekonomi dan Bisnis": ["Manajemen", "Akuntansi", "Ekonomi Pembangunan"],
    "Fakultas Kedokteran": ["Pendidikan Dokter", "Farmasi", "Ilmu Keperawatan"],
    "Fakultas Hukum": ["Ilmu Hukum"]
}
JALUR_MASUK = ["SNMPTN", "SBMPTN", "Mandiri", "Internasional"]
SUMBER_BIAYA = ["Orang Tua", "Beasiswa", "KIP-K", "Mandiri"]
AGAMA = ["Islam", "Kristen", "Katolik", "Hindu", "Buddha", "Konghucu"]
JABATAN_PRESTASI = ["Juara 1", "Juara 2", "Juara 3", "Finalis", "Peserta"]
TINGKAT_PRESTASI = ["Internasional", "Nasional", "Provinsi", "Kabupaten/Kota", "Universitas"]
KELOMPOK_KEGIATAN = ["Ilmiah", "Olahraga", "Seni", "Sosial", "Kewirausahaan"]
DEPARTMENTS = list(FAKULTAS_PRODI.keys())
TITLES = ["Professor", "Associate Professor", "Assistant Professor", "Lecturer", "Senior Lecturer"]

def generate_mahasiswa_data(num_records):
    print(f"Generating {num_records} mahasiswa records...")
    mahasiswa_list = []
    nim_set = set()
    current_year = datetime.datetime.now().year
    
    while len(mahasiswa_list) < num_records:
        angkatan = random.randint(current_year - 5, current_year)
        fakultas = random.choice(list(FAKULTAS_PRODI.keys()))
        prodi = random.choice(FAKULTAS_PRODI[fakultas])
        
        # Generate a unique NIM
        nim = f"{angkatan % 100}{random.randint(10, 99)}{len(mahasiswa_list)+1:05d}"
        if nim in nim_set:
            continue
        nim_set.add(nim)
        
        tgl_lahir = fake.date_of_birth(minimum_age=17, maximum_age=25)
        
        mahasiswa_list.append((
            nim, fake.name(), fake.city(), tgl_lahir,
            random.choice(JALUR_MASUK), "Regular", fake.address(),
            fakultas, prodi, 'A', random.choice(SUMBER_BIAYA), "Aktif",
            angkatan, random.choice(['L', 'P']), 'S1', fake.city(),
            fake.state(), "Indonesia", "WNI", random.randint(1, 50) * 1000000,
            "Indonesia", random.choice(AGAMA), f"UKT {random.randint(1, 7)}",
            random.choice(["Ya", "Tidak"])
        ))
    return mahasiswa_list

def generate_faculty_data(num_records):
    print(f"Generating {num_records} faculty records...")
    faculty_list = []
    for i in range(1, num_records + 1):
        name = fake.name()
        email = f"{name.lower().replace(' ', '.')}{i}@university.edu"
        faculty_list.append((
            i, name, email, random.choice(DEPARTMENTS),
            random.choice(TITLES), fake.date_between(start_date='-20y', end_date='-1y')
        ))
    return faculty_list

def generate_publications_data(faculty_ids):
    print("Generating publications records...")
    publications_list = []
    pub_id_counter = 1
    for fac_id in faculty_ids:
        num_pubs = random.randint(NUM_PUBLICATIONS_PER_FACULTY[0], NUM_PUBLICATIONS_PER_FACULTY[1])
        for _ in range(num_pubs):
            publications_list.append((
                pub_id_counter, fake.sentence(nb_words=8), fac_id,
                fake.company() + " Journal", random.randint(2010, 2023),
                random.randint(0, 300)
            ))
            pub_id_counter += 1
    return publications_list

def generate_prestasi_data(mahasiswa_records):
    print("Generating prestasi records...")
    prestasi_list = []
    num_prestasi = int(len(mahasiswa_records) * PRESTASI_RATIO)
    mahasiswa_sample = random.sample(mahasiswa_records, num_prestasi)
    
    for mhs in mahasiswa_sample:
        nim = mhs[0]
        nama = mhs[1]
        jenjang = mhs[14]
        prodi = mhs[8]
        fakultas = mhs[7]
        tahun_ajaran_start = mhs[12]
        
        prestasi_list.append((
            nim, nama, jenjang, prodi, fakultas,
            f"Prestasi di {fake.company()}",
            random.randint(tahun_ajaran_start, datetime.datetime.now().year),
            f"{tahun_ajaran_start}/{tahun_ajaran_start + 1}",
            random.choice(["Ganjil", "Genap"]),
            random.choice(JABATAN_PRESTASI),
            random.choice(TINGKAT_PRESTASI),
            f"Kegiatan {fake.bs()}",
            random.choice(KELOMPOK_KEGIATAN),
            str(fake.date_this_decade()),
            None, None, fake.name(), None, None, None, None, None, fake.company()
        ))
    return prestasi_list

def main():
    conn = None
    try:
        print("Connecting to the database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Generate all data first
        mahasiswa_data = generate_mahasiswa_data(NUM_MAHASISWA)
        faculty_data = generate_faculty_data(NUM_FACULTY)
        faculty_ids = [f[0] for f in faculty_data]
        publications_data = generate_publications_data(faculty_ids)
        prestasi_data = generate_prestasi_data(mahasiswa_data)
        
        # Insert data using execute_batch for efficiency
        print("\nStarting data insertion...")
        start_time = time.time()

        print("Inserting into public.mahasiswa...")
        psycopg2.extras.execute_batch(cur, "INSERT INTO public.mahasiswa VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", mahasiswa_data)
        
        print("Inserting into public.faculty...")
        psycopg2.extras.execute_batch(cur, "INSERT INTO public.faculty VALUES (%s, %s, %s, %s, %s, %s)", faculty_data)
        
        print("Inserting into public.publications...")
        psycopg2.extras.execute_batch(cur, "INSERT INTO public.publications VALUES (%s, %s, %s, %s, %s, %s)", publications_data)

        print("Inserting into public.prestasi_mawa...")
        psycopg2.extras.execute_batch(cur, "INSERT INTO public.prestasi_mawa VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", prestasi_data)

        print("Committing transaction...")
        conn.commit()
        
        end_time = time.time()
        print(f"\nSuccessfully populated the database in {end_time - start_time:.2f} seconds.")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"\nError connecting to or populating PostgreSQL database: {error}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main()
