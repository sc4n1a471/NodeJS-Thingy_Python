import urllib.request
import time
import os

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By

from application.data import settings
from application.data.xpaths import XPATHS
from application.models.Inspection import Inspection


def get_images(car):
    """
    Downloads images associated to the inspections
    :param car: car object
    """
    # WebDriverWait(settings.driver, 5).until(ec.presence_of_element_located((By.XPATH, XPATHS.get("inspections_tab"))))
    settings.driver.find_element(By.XPATH, XPATHS.get("inspections_tab")).click()
    print("CLICKED: Condition Inspections")

    if len(settings.driver.find_elements(By.XPATH, XPATHS.get('no_inspection_data'))) != 0:
        print("NOT FOUND: Inspection data")
    else:
        car_inspections: [Inspection] = []

        WebDriverWait(settings.driver, 3).until(ec.presence_of_element_located((By.XPATH, XPATHS.get("inspections"))))

        inspections = settings.driver.find_elements(By.XPATH, XPATHS.get('inspections'))
        for (inspection_data, i) in zip(inspections, range(0, len(inspections))):
            if i != 0:  # the first inspection is open on tab change
                inspection_data.click()
            car_inspections.append(Inspection(inspection_data.text))
            time.sleep(0.4)

        counter = 0
        while counter < 5:
            try:
                show_pictures_buttons = settings.driver \
                    .find_elements(By.XPATH, XPATHS.get('inspections_show_pictures'))
                show_pictures_buttons.pop(0)
                counter = 6
            except:
                counter += 1
                time.sleep(0.25)

        if counter == 5:
            return

        for (button, i) in zip(show_pictures_buttons, range(0, len(inspections) + 1)):
            images = []

            button.click()

            settings.driver.switch_to.default_content()
            dialog_frame = settings.driver \
                .find_element(By.XPATH, XPATHS.get('inspections_pictures_dialog_frame'))
            settings.driver.switch_to.frame(dialog_frame)
            print('Switched iframe to dialog_frame')

            try:
                WebDriverWait(settings.driver, 2).until(
                    ec.presence_of_element_located((By.XPATH, XPATHS.get('inspections_no_pictures')))
                )
                # time.sleep(1)
            except:
                WebDriverWait(settings.driver, 7).until(
                    ec.presence_of_element_located((By.XPATH, XPATHS.get('inspections_pictures')))
                )

                imgs = settings.driver.find_elements(By.XPATH, XPATHS.get('inspections_pictures'))

                for img in imgs:
                    src = img.get_attribute('src')
                    replaced_src = src.replace("data:image/jpeg;base64,", "")
                    if not replaced_src in images:
                        images.append(replaced_src)
                        print("Added image to array...")

                car_inspections[i].images = images

            WebDriverWait(settings.driver, 4).until(
                ec.presence_of_element_located((By.XPATH, XPATHS.get('inspections_close_button')))
            )
            close_dialog_button = settings.driver \
                .find_element(By.XPATH, XPATHS.get('inspections_close_button'))
            close_dialog_button.click()

            settings.driver.switch_to.default_content()
            iframe = settings.driver \
                .find_element(By.XPATH, XPATHS.get('main_frame'))
            settings.driver.switch_to.frame(iframe)
            print("Switched to main iframe")

        car.inspections = car_inspections
        save_images(car.license_plate, car.inspections)


def save_images(license_plate, inspections):
    """Saves the image files into folders"""
    print("Saving images...")

    if not os.path.exists('downloaded_images'):
        print("downloaded_images folder does not exist, not saving images...")
        # try:
        #     os.mkdir('downloaded_images')
        # except Exception as exc:
        #     print(f"Folder creation for downloaded_images failed, error: {exc}")
        #     return
        return

    license_plate_path = os.path.join('downloaded_images', license_plate)
    try:
        os.mkdir(license_plate_path)
    except Exception as exc:
        print(f"Folder creation for license plate ({license_plate_path}) failed, error: {exc}")
        return

    for inspection in inspections:
        inspection_path = os.path.join(license_plate_path, inspection.name)

        try:
            os.mkdir(inspection_path)
        except Exception as exc:
            print(f"Folder creation for inspection ({inspection_path}) failed, error: {exc}")
            continue

        counter = 0
        for image_src in inspection.images:
            if image_src is None:
                continue
            image_path = os.path.join(inspection_path, f'{counter}.jpg')
            urllib.request.urlretrieve("data:image/jpeg;base64," + image_src, image_path)
            counter += 1
