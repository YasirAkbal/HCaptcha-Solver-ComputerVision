import numpy as np
import cv2
from keras import models
from keras import layers
import os
import matplotlib.pyplot as plt
from selenium import webdriver
import time
import requests
import glob
from selenium.common import exceptions

class HCap:
    __model = models.load_model("effinetHcap.h5")
    __uniqAdlar = {'araba':0,'bisiklet':1,
           'kamyon':2,'motosiklet':3,'motorbus':4,'tekne':5,'tren':6,'ucak':7}
    __site_to_veriseti = {"araba":"araba","bisiklet":"bisiklet","bot":"tekne","kamyon":"kamyon","motor otobüsü":"motorbus",
    "motorbus":"motorbus","motosiklet":"motosiklet","tekne":"tekne","tren":"tren","uçak":"ucak"}

    def __init__(self,YOL,browser,bilgi_satir,resimleri_kapsayan_divler,sonraki_atla,noktalar,hata_mesaji):
        self.yol = YOL
        self.browser = browser
        self.bilgi_satir = bilgi_satir
        self.resimleri_kapsayan_divler = resimleri_kapsayan_divler
        self.sonraki_atla = sonraki_atla
        self.noktalar = noktalar
        self.hata_mesaji = hata_mesaji

    def checkboxa_tikla(self,iframe1,iframe2):
        self.browser.switch_to.frame(self.browser.find_element_by_xpath(iframe1))
        time.sleep(1.0)

        checkbox = self.browser.find_element_by_id("checkbox")
        checkbox.click()
        time.sleep(0.7)

        self.browser.switch_to.parent_frame()
        time.sleep(0.7)

        self.browser.switch_to.frame(self.browser.find_element_by_xpath(iframe2))
        time.sleep(0.7)

    def calis(self):
        sayfa_sayisi = self.sayfaSayisiniBul()
        if (sayfa_sayisi == 0):
            sayfa_sayisi = 1
        tumResimler = np.empty((sayfa_sayisi * 9, 196, 196, 3))
        bilgi_satir = self.browser.find_element_by_xpath(self.bilgi_satir).text
        for i in range(sayfa_sayisi):
            # kapsayici divleri al
            resimlerDivTemp = list()
            for j in range(9):
                resimlerDivTemp.append(
                    self.browser.
                        find_element_by_xpath(self.resimleri_kapsayan_divler.format(j + 1)))

            # kapsayici divden linkleri al
            resimLinkleriTemp = list()
            for resimDiv in resimlerDivTemp:
                eleman = resimDiv.find_element_by_css_selector("div.image-wrapper > div")
                style = eleman.get_attribute("style")
                link = self.url_ayikla(style)
                # print(link)
                resimLinkleriTemp.append(link)

            if (self.indir(resimLinkleriTemp, self.yol, i * 9 + 1)):
                resimler = self.resimleri_oku(i * 9 + 1, i * 9 + 10, self.yol)
                tumResimler[i * 9:i * 9 + 9] = resimler
                sonuclar = self.__model.predict(resimler)
                siniri_gecen_varmi=False;
                for k, sonuc in enumerate(sonuclar):
                    #tahmin_k = list(self.uniqAdlar.keys())[sonuc.argmax()]
                    temp = self.__site_to_veriseti[self.istenilen_nesneyi_bul(bilgi_satir)]
                    if (sonuc[self.__uniqAdlar[temp]] > 0.4):
                        resimlerDivTemp[k].click()
                        time.sleep(0.3)
                        siniri_gecen_varmi=True
                        print(k)
                if(not siniri_gecen_varmi):
                    temp = self.__site_to_veriseti[self.istenilen_nesneyi_bul(bilgi_satir)]
                    max = np.argmax(sonuclar[:,self.__uniqAdlar[temp]])
                    resimlerDivTemp[max].click()
                sonrakiButton = self.browser.find_element_by_xpath(self.sonraki_atla)
                sonrakiButton.click()
                time.sleep(1.5)
        self.klasoru_temizle()

    def resimleri_oku(self,bas, son, yol):
        walk = os.walk(yol)
        yol, klasorler, dosyalar = next(walk)
        resimler = np.empty((9, 196, 196, 3))
        for i in range(9):
            resim = cv2.imread(yol + "\\" + str(bas) + ".png") / 255.
            resim = cv2.resize(resim, (196, 196))
            resimler[i] = resim
            bas += 1
        return resimler

    def sayfaSayisiniBul(self):
        noktalar = self.browser.find_elements_by_css_selector(self.noktalar)
        return len(noktalar)

    def indir(self,linkler, yol, indis=1):
        for link in linkler:
            # print(link)
            r = requests.get(link)
            ad = str(indis) + ".png"
            with open(yol + "\\" + ad, "wb") as dosya:
                dosya.write(r.content)
            indis += 1
        return True

    def url_ayikla(self,link):
        temp_indis = link.find("url")
        bas_indis = temp_indis + 5
        son_indis = link.find('")', bas_indis)
        return link[bas_indis:son_indis]

    def istenilen_nesneyi_bul(self,satir):
        parcalar = satir.split()
        if (satir[:11] == "Lütfen bir " or satir[:14] == "Lütfen içinde "):
            if (parcalar[3] == "içeren" or parcalar[3] == "bulunan"):
                return parcalar[2]
            else:
                return parcalar[2] + " " + parcalar[3]
        elif (satir[:7] == "Lütfen "):
            if (parcalar[2] == "içeren" or parcalar[2] == "bulunan"):
                return parcalar[1]
            else:
                return parcalar[1] + " " + parcalar[2]

    def hatali_mi(self,browser):
        div = browser.find_element_by_xpath(self.hata_mesaji)
        style = div.get_attribute("style")
        if (style.find("opacity: 1;") == -1):
            return False
        return True

    def klasoru_temizle(self):
        files = glob.glob(self.yol + "/*")
        for f in files:
            os.remove(f)