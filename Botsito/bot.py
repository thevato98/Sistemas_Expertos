
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def verificar_disponibilidad_liverpool(url_producto):
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 30)

    resultados = []

    try:
        driver.get(url_producto)
        ver_disp_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.btnGeoStore")))
        ver_disp_btn.click()


        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "a-product__anchorSelectState")))
        estados = driver.find_elements(By.CLASS_NAME, "a-product__anchorSelectState")

        nombres_estados = [estado.text.strip() for estado in estados if estado.text.strip()]

        for nombre_estado in nombres_estados:
            print(f"🔄 Verificando estado: {nombre_estado}")
            try:

                if not driver.find_elements(By.CLASS_NAME, "a-product__anchorSelectState"):
                    ver_disp_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.btnGeoStore")))
                    ver_disp_btn.click()
                    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "a-product__anchorSelectState")))


                estado_btn = driver.find_element(
                    By.XPATH,
                    f"//a[contains(@class, 'a-product__anchorSelectState') and contains(text(),'{nombre_estado}')]"
                )
                estado_btn.click()


                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.a-product__store")))
                tiendas = driver.find_elements(By.CSS_SELECTOR, "div.a-product__store")

                for tienda in tiendas:
                    try:
                        nombre_tienda = tienda.find_elements(By.TAG_NAME, "p")[0].text.strip()
                        stock = tienda.find_elements(By.TAG_NAME, "p")[1].text.strip()
                        resultados.append({
                            "Estado": nombre_estado,
                            "Tienda": nombre_tienda,
                            "Stock": stock
                        })
                    except Exception as e:
                        print(f"❌ Error leyendo tienda en {nombre_estado}: {e}")


                time.sleep(2)

            except Exception as e:
                print(f"⚠️ No se pudo obtener información de {nombre_estado}: {e}")


        with open("disponibilidad_todos_estados.csv", "w", newline="", encoding="utf-8") as archivo:
            writer = csv.DictWriter(archivo, fieldnames=["Estado", "Tienda", "Stock"])
            writer.writeheader()
            writer.writerows(resultados)

        print("✅ Datos guardados en 'disponibilidad_todos_estados.csv'")

    finally:
        driver.quit()

if __name__ == "__main__":
    url = "https://www.liverpool.com.mx/tienda/pdp/consola-xbox-series-x-de-1-tb-edición-digital/1163093606?skuid=1163093606"
    verificar_disponibilidad_liverpool(url)
