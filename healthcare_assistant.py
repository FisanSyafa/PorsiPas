import streamlit as st
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv
import os
from PIL import Image
import re

st.set_page_config(page_title="PorsiPas", layout="wide")
load_dotenv()


@st.cache_data(show_spinner="Memuat semua database gizi...")
def load_all_nutrition_data(files):
    all_dfs = []
    for file in files:
        try:
            df = pd.read_csv(file)
            rename_map = {
                'Food': 'Food', 'Measure': 'Measure', 'Calories': 'Calories', 
                'Protein': 'Protein', 'Fat': 'Fat', 'Carbs': 'Carbs',
                'Item': 'Food', 'Serving Size': 'Measure', 'Protein (g)': 'Protein',
                'Total Fat (g)': 'Fat', 'Carbohydrates (g)': 'Carbs',
                'name': 'Food', 'calories': 'Calories', 'proteins': 'Protein',
                'fat': 'Fat', 'carbohydrate': 'Carbs'
            }
            df.rename(columns=lambda col: rename_map.get(col, col), inplace=True)

            if 'Food' in df.columns:
                df.dropna(subset=['Food'], inplace=True)
                all_dfs.append(df)
        except FileNotFoundError:
            pass
        except Exception as e:
            st.error(f"Gagal memuat {file}: {e}")
    
    if not all_dfs:
        st.error("Tidak ada file database gizi yang berhasil dimuat.")
        return None, None
        
    combined_df = pd.concat(all_dfs, ignore_index=True)
    food_names_list = combined_df['Food'].dropna().unique().tolist()
    return combined_df, food_names_list

def keyword_search_retriever(df, query, top_k=1):
    results = df[df['Food'].str.contains(query, case=False, na=False)]
    
    if results.empty and len(query.split()) > 1:
        first_word = query.split()[0]
        results = df[df['Food'].str.contains(first_word, case=False, na=False)]

    if results.empty:
        return None, None
    
    top_result = results.head(top_k)
    food_name_detected = top_result['Food'].iloc[0]
    
    context = ""
    for index, row in top_result.iterrows():
        context += f"Data Nutrisi untuk '{query}':\n"
        context += f"- Makanan Ditemukan: {row.get('Food', 'N/A')}\n"
        context += f"- Ukuran Saji: {row.get('Measure', 'N/A')}\n"
        context += f"- Kalori: {row.get('Calories', 'N/A')}\n"
        context += f"- Protein (g): {row.get('Protein', 'N/A')}\n"
        context += f"- Lemak (g): {row.get('Fat', 'N/A')}\n"
        context += f"- Karbohidrat (g): {row.get('Carbs', 'N/A')}\n"
        context += "---\n"
        
    return food_name_detected, context

def generate_final_response(context, simple_food_names):

    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    
    prompt = f"""
    Anda adalah seorang ahli gizi dan perencana menu makanan. Berdasarkan data nutrisi spesifik yang saya berikan, buatlah jawaban dengan mengikuti FORMAT WAJIB berikut:

    **Nama Makanan:**
    {', '.join(simple_food_names)}

    **Detail Nutrisi Gabungan:**
    [Analisis dan rangkum total/rata-rata nutrisi dari semua data yang ada di bagian "Data Nutrisi yang Ditemukan". Sajikan dalam bentuk poin-poin ringkas.]

    **Analisis & Rekomendasi Menu Berikutnya:**
    [Berdasarkan ringkasan nutrisi di atas, berikan analisis singkat.]
    [Selanjutnya, berikan rekomendasi menu spesifik untuk **makanan berikutnya** (misal: makan malam) untuk menyeimbangkan asupan gizi. Sarankan 1-2 contoh menu lengkap.]
    ---
    Data Nutrisi yang Ditemukan:
    {context}
    ---
    PENTING: Untuk bagian "Nama Makanan", gunakan daftar nama yang telah saya berikan di atas, bukan nama spesifik dari "Data Nutrisi yang Ditemukan".
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error saat menghasilkan jawaban: {e}"

def extract_foods_with_gemini(user_input, food_names_list):
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    food_context = ", ".join(food_names_list[:500])

    prompt = f"""
    Dari "Kalimat Pengguna" berikut, ekstrak SEMUA nama makanan yang disebutkan.
    Hasilnya HARUS berupa daftar yang dipisahkan koma.
    Contoh:
    Kalimat Pengguna: "pagi saya makan opor, siang sop, malam nasi goreng"
    Jawaban Anda: opor, sop, nasi goreng
    ---
    Kalimat Pengguna: "{user_input}"
    Daftar Makanan yang Dikenal (sebagian): "{food_context}"
    ---
    Jawaban Anda (hanya nama makanan dipisahkan koma):
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        st.error(f"Gagal mengekstrak makanan: {e}")
        return ""

def get_food_name_from_image(image, question):
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    try:
        response = model.generate_content([question, image])
        return response.text.strip()
    except Exception as e:
        return f"Error saat memproses gambar: {e}"

# Streamlit
with st.sidebar:
    st.header("Konfigurasi")
    api_key_input = st.text_input("Masukkan Google API Key Anda:", type="password", key="api_key_input")
    if st.button("Konfirmasi API Key", use_container_width=True):
        if api_key_input:
            st.session_state['google_api_key'] = api_key_input
            st.success("API Key berhasil dikonfirmasi!")
        else:
            st.warning("Mohon masukkan API Key Anda.")

st.title("PorsiPas - Asisten penyeimbang gizi")
st.markdown("Analisis menu harian Anda untuk mengukur gizi dan memberikan rekomendasi menu lanjutan agar gizi seimbang.")

if 'google_api_key' in st.session_state and st.session_state['google_api_key']:
    try:
        genai.configure(api_key=st.session_state['google_api_key'])
        csv_files = ["nutrients.csv", "dishes.csv", "fastfood.csv", "nutrition.csv"]
        df_nutrition, all_food_names = load_all_nutrition_data(csv_files)

        if df_nutrition is not None:
            st.subheader("Masukkan Menu Harian Anda")
            col1, col2 = st.columns(2)
            with col1:
                text_query = st.text_area("Ketik dalam kalimat biasa:", placeholder="Contoh: pagi ini saya makan soto ayam dan rendang")
                analyze_text_button = st.button("Analisis Teks", use_container_width=True)
            with col2:
                uploaded_image = st.file_uploader("Atau unggah foto satu jenis makanan:")
                analyze_image_button = st.button("Analisis Gambar", use_container_width=True)

            st.markdown("---")
            if "messages" not in st.session_state:
                st.session_state.messages = [{"role": "assistant", "content": "Halo! Saya siap menganalisis menu Anda."}]

            if analyze_text_button and text_query:
                with st.spinner("Menganalisis..."):
                    extracted_foods_str = extract_foods_with_gemini(text_query, all_food_names)
                    if extracted_foods_str:
                        st.info(f"Makanan yang terdeteksi dari kalimat Anda: **{extracted_foods_str}**")
                        food_list = [food.strip() for food in extracted_foods_str.split(',') if food.strip()]
                        
                        aggregated_context = ""
                        foods_found_simple_names = []
                        foods_not_found = []

                        for food in food_list:
                            food_name_detected, context = keyword_search_retriever(df_nutrition, food)
                            if context:
                                aggregated_context += context
                                foods_found_simple_names.append(food)
                            else:
                                foods_not_found.append(food)
                        
                        if foods_not_found:
                            st.warning(f"Data tidak ditemukan untuk: {', '.join(foods_not_found)}")

                        if aggregated_context:
                            ai_response = generate_final_response(aggregated_context, foods_found_simple_names)
                            st.session_state.messages.append({"role": "user", "content": text_query})
                            st.session_state.messages.append({"role": "assistant", "content": ai_response})
                            st.rerun()

            if analyze_image_button and uploaded_image:
                with st.spinner("Menganalisis..."):
                    image_for_model = Image.open(uploaded_image)
                    prompt_vision = "Identifikasi makanan utama dalam gambar ini. Jawab hanya dengan nama makanannya."
                    detected_food_name = get_food_name_from_image(image_for_model, prompt_vision)
                    
                    food_name_from_db, context = keyword_search_retriever(df_nutrition, detected_food_name)
                    if context:
                        st.info(f"Gambar terdeteksi sebagai '{detected_food_name}', data ditemukan untuk: **{food_name_from_db}**")
                        ai_response = generate_final_response(context, [detected_food_name])
                        st.session_state.messages.append({"role": "user", "content": f"Analisis gizi dari gambar (terdeteksi: {detected_food_name})."})
                        st.session_state.messages.append({"role": "assistant", "content": ai_response})
                        st.rerun()
                    else:
                        st.warning(f"Makanan terdeteksi sebagai '{detected_food_name}', namun datanya tidak ditemukan.")

            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
else:
    st.info("👈 Silakan masukkan dan konfirmasi Google API Key Anda di sidebar untuk memulai.")