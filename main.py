from HCapCozucu import HCap
from selenium import webdriver
import time

YOL = "indirilenler"
URL = "http://democaptcha.com/demo-form-eng/hcaptcha.html"
IFRAME1 = "/html/body/main/article/div/form/div/iframe"
IFRAME2= "/html/body/div[2]/div[1]/iframe"
BILGISATIR = "/html/body/div[1]/div/div/div[1]/div[1]/div[1]/div[1]"
RESIMLERIKAPSAYANDIVLER = "/html/body/div[1]/div/div/div[2]/div[{0}]"
SONRAKIATLA = "/html/body/div[2]/div[8]"
NOKTALAR = "body > div.challenge-interface > div.challenge-breadcrumbs > div > div"
HATAMESAJI = "/html/body/div[2]/div[4]"

browser = webdriver.Firefox()
h = HCap(YOL,browser,BILGISATIR,RESIMLERIKAPSAYANDIVLER,SONRAKIATLA,NOKTALAR,HATAMESAJI)
browser.get(URL)
time.sleep(1.0)
h.checkboxa_tikla(IFRAME1,IFRAME2)

h.calis()

