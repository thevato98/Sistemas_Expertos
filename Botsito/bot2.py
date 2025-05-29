import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
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


        cerrar_modal(driver, wait)

        print(f"📋 Estados encontrados: {len(nombres_estados)}")
        print(f"🗂️ Lista de estados: {', '.join(nombres_estados)}")


        for i, nombre_estado in enumerate(nombres_estados, 1):
            print(f"\n🔄 Procesando estado {i}/{len(nombres_estados)}: {nombre_estado}")

            try:

                abrir_modal_disponibilidad(driver, wait)


                estado_btn = wait.until(EC.element_to_be_clickable((
                    By.XPATH,
                    f"//a[contains(@class, 'a-product__anchorSelectState') and contains(text(),'{nombre_estado}')]"
                )))
                estado_btn.click()


                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.a-product__store")))
                time.sleep(2)


                tiendas = driver.find_elements(By.CSS_SELECTOR, "div.a-product__store")
                print(f"   🏪 Tiendas encontradas: {len(tiendas)}")

                for j, tienda in enumerate(tiendas, 1):
                    try:
                        paragrafos = tienda.find_elements(By.TAG_NAME, "p")
                        if len(paragrafos) >= 2:
                            nombre_tienda = paragrafos[0].text.strip()
                            stock = paragrafos[1].text.strip()

                            resultado = {
                                "Estado": nombre_estado,
                                "Tienda": nombre_tienda,
                                "Stock": stock
                            }
                            resultados.append(resultado)
                            print(f"   ✅ Tienda {j}: {nombre_tienda} - {stock}")
                        else:
                            print(f"   ⚠️ Tienda {j}: Información incompleta")

                    except Exception as e:
                        print(f"   ❌ Error leyendo tienda {j} en {nombre_estado}: {e}")


                cerrar_modal(driver, wait)
                print(f"   🔒 Modal cerrado para {nombre_estado}")

                time.sleep(1)

            except Exception as e:
                print(f"⚠️ Error procesando {nombre_estado}: {e}")
                try:
                    cerrar_modal(driver, wait)
                except:
                    pass


        if resultados:
            guardar_csv(resultados)
            print(f"\n✅ Proceso completado. {len(resultados)} registros guardados en CSV")
        else:
            print("\n⚠️ No se encontraron datos para guardar")

    except Exception as e:
        print(f"❌ Error general: {e}")
    finally:
        driver.quit()


def abrir_modal_disponibilidad(driver, wait):

    try:
        ver_disp_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.btnGeoStore")))
        ver_disp_btn.click()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "a-product__anchorSelectState")))
        time.sleep(1)
    except Exception as e:
        print(f"❌ Error abriendo modal: {e}")
        raise


def cerrar_modal(driver, wait):

    try:

        try:
            close_btn = driver.find_element(By.CSS_SELECTOR,
                                            "button.close, .modal-close, [aria-label='Close'], .btn-close")
            close_btn.click()
            time.sleep(1)
            return
        except:
            pass


        try:
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            time.sleep(1)
            return
        except:
            pass


        try:
            overlay = driver.find_element(By.CSS_SELECTOR, ".modal-backdrop, .overlay, .modal-overlay")
            overlay.click()
            time.sleep(1)
            return
        except:
            pass


        try:
            body = driver.find_element(By.TAG_NAME, "body")
            driver.execute_script("arguments[0].click();", body)
            time.sleep(1)
        except:
            pass

    except Exception as e:
        print(f"⚠️ Advertencia cerrando modal: {e}")


def guardar_csv(resultados):

    try:
        filename = f"disponibilidad_liverpool_{int(time.time())}.csv"
        with open(filename, "w", newline="", encoding="utf-8") as archivo:
            writer = csv.DictWriter(archivo, fieldnames=["Estado", "Tienda", "Stock"])
            writer.writeheader()
            writer.writerows(resultados)
        print(f"📄 Archivo guardado: {filename}")
    except Exception as e:
        print(f"❌ Error guardando CSV: {e}")


if __name__ == "__main__":
    url = "https://www.liverpool.com.mx/tienda/pdp/apple-iphone-15-6.1-pulgadas-super-retina-xdr/1142680818?skuid=1142576364"
    verificar_disponibilidad_liverpool(url)