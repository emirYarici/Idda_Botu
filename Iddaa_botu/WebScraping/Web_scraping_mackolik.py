from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from bs4 import BeautifulSoup
import mysql.connector
import requests
import datetime
#databas bağlantısı
maclarin_oranlari_listesi = []
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Emireren1",
    database="ysa_proje"
)

#skor yardımı ile labellama yapılıyor
def label_satirla(id, iy_ev, iy_dep, ms_ev, ms_dep):
    # 63
    iddaa_basliklari = {'ms1': 0, 'msx': 0, 'ms2': 0,
                        'msalt': 0, 'msust': 0,
                        'iy1': 0, 'iyx': 0, 'iy2': 0,
                        'var': 0, 'yok': 0,
                        '1_1': 0, 'x_1': 0, '2_1': 0, '1_x': 0, 'x_x': 0, '2_x': 0, '1_2': 0, 'x_2': 0, '2_2': 0,
                        'hdep1': 0, 'hdepx': 0, 'hdep2': 0,
                        'hev1': 0, 'hevx': 0, 'hev2': 0,
                        '0-0': 0, '0-1': 0, '0-2': 0, '0-3': 0, '0-4': 0, '0-5': 0, '1-0': 0, '1-1': 0, '1-2': 0,
                        '1-3': 0, '1-4': 0, '1-5': 0, '2-0': 0,
                        '2-1': 0, '2-2': 0, '2-3': 0, '2-4': 0, '0-6': 0, '3-0': 0, '3-1': 0, '3-2': 0, '3-3': 0,
                        '4-0': 0, '4-1': 0, '4-2': 0, '5-0': 0, '5-1': 0, '6-0': 0,
                        '1-alt': 0, 'x-alt': 0, '2-alt': 0,
                        '1-ust': 0, 'x-ust': 0, '2-ust': 0}
    mac_sonucu = ""
    # ilk yari duzenlemeleri
    # iys iycş
    if iy_ev > iy_dep:
        iy_sonucu = "1"

    elif iy_ev == iy_dep:
        iy_sonucu = "x"

    else:
        iy_sonucu = "2"

    iddaa_basliklari['iy' + iy_sonucu] = 1

    # mac sonu duzenlemeleri

    # h , cifte sans
    if ms_ev > ms_dep:
        mac_sonucu = "1"
        iddaa_basliklari['hev1'] = 1

        if ms_ev > ms_dep + 1:
            iddaa_basliklari['hdep1'] = 1
        else:
            iddaa_basliklari['hdepx'] = 1

    elif ms_ev == ms_dep:
        mac_sonucu = "x"
        iddaa_basliklari['hev1'] = 1
        iddaa_basliklari['hdep2'] = 1

    else:
        mac_sonucu = "2"
        iddaa_basliklari['hdep2'] = 1

        if ms_ev > ms_dep + 1:
            iddaa_basliklari['hev2'] = 1
        else:
            iddaa_basliklari['hevx'] = 1
    # ms , iy/ms skor
    iddaa_basliklari['ms' + mac_sonucu] = 1
    iddaa_basliklari[iy_sonucu + "_" + mac_sonucu] = 1
    if ms_ev + ms_dep <= 6:
        skor = str(ms_ev) + "-" + str(ms_dep)
        iddaa_basliklari[skor] = 1
    # alt ust ve ms alt ust
    if ms_dep + ms_ev > 2:
        iddaa_basliklari['msust'] = 1
        iddaa_basliklari[mac_sonucu + '-ust'] = 1
    else:
        iddaa_basliklari['msalt'] = 1
        iddaa_basliklari[mac_sonucu + '-alt'] = 1
    # var - yok
    if ms_dep > 0 and ms_ev > 0:
        iddaa_basliklari['var'] = 1
    else:
        iddaa_basliklari['yok'] = 1
    say = 0
    basliklar = list(iddaa_basliklari)

    query = "INSERT INTO tbl_labellar values(" + str(id)
    for baslik in basliklar:
        query += "," + str(iddaa_basliklari[baslik])

    query += ")"
    print(query)
    cur = mydb.cursor()
    cur.execute(query)
    mydb.commit()
    cur.close()


# tarih ayarlanmasi
with open("Tarihler.txt", 'r', encoding='utf-8') as f:
    for line in f:
        date = line
"""
2021-02-12 gunu dahil cektim 
2022-1-08 dahil ust sinir
"""
yil, ay, gun = tuple(date.split('-'))
date = datetime.datetime(int(yil), int(ay), int(gun))
date = date - datetime.timedelta(days=1)
# ıd ayarlanması
query = "SELECT count(*) FROM ysa_proje.tbl_maclar"
cur = mydb.cursor()
cur.execute(query)
rows = cur.fetchall()
for row in rows:
    id = row
cur.close()
id = id[0] + 2000
url = 'https://www.mackolik.com/futbol/canli-sonuclar'
while 1:
    driver = webdriver.Chrome(executable_path="C:\\Users\\Hp\\Desktop\\chromedriver")
    driver.get(url)
    try:
        while True:
            gecilen_mac = 0
            str_date = date.strftime('%Y-%m-%d')
            with open("Tarihler.txt", 'w', encoding='utf-8') as f:
                f.write(str_date)
            print(str_date + "**********************************************************" * 40)
            iddaa_kodlari = {'1': 3, '4': 3, '6-11': 3, '611': 3, '11': 2, '15': 28, '62': 6, '14': 9, '18': 2}
            istenen_yok = False
            print("---------------------*-*---------------------------------*-*---------------------------")
            while 1:
                try:
                    #gun degerine tiklamayı dene
                    driver.find_element_by_xpath('//*[@id="widget-dateslider-day-' + str_date + '"]').click()
                    break
                    #araya reklam girerse
                except ElementClickInterceptedException:
                    driver.find_element_by_xpath('//*[@id="close47559333074953319"]').click()
                    #tarih listesinde istedigin gun yoksa
                except NoSuchElementException:
                    try:
                        #previous tusuna basmayı dene
                        driver.find_element_by_xpath(
                            "/html/body/div[4]/div/main/div/div[1]/div[1]/div[1]/div[1]/button[1]").click()
                    #reklam cıkarsa
                    except:

                        driver.find_element_by_xpath('//*[@id="close47559333074953319"]').click()
                    #sayfa dinamik olarak yuklendiğinden biraz beklemek gerekiyor
                    try:
                        myElem = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.ID, 'id="widget-dateslider-day-' + str_date + "'")))
                        print("Page is ready!")
                    except TimeoutException:
                        print("Loading took too much time!")
            try:
                myElem = WebDriverWait(driver, 90).until(
                    EC.presence_of_element_located((By.ID, 'id="widget-dateslider-day-' + str_date + "'")))
                print("Page is ready!")
            except TimeoutException:
                print("Loading took too much time!")
            #simdi selenium u bırakıp BeautifulSoup kullanmaya başladık
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            #gunun tum maç adreslerini veren href adresleri su an mac_html_adresleri degiskenine atandı
            mac_html_adresleri = soup.find_all('a', class_="match-row__score", href=True)

            #o gunun her macı icin asağıdaki islemler yapılacak, ancak istenen 67 ozniteliğe sahip degilse bu mac
            #gecilecek
            for adres in mac_html_adresleri:

                query = "INSERT INTO tbl_maclar values"
                istenen_yok = False
                bolumler = str(adres['href']).split("/")
                mac_ismi = bolumler[4]  # 7422395 7428335 7428328 7428149 7531691 7428338 7428340
                del bolumler[5]
                bolumler.insert(-1, "iddaa")
                iddaa_html_adress = "/".join([str(item) for item in bolumler])
                iddaa_html_adress = requests.get(iddaa_html_adress).text
                iddaa_sayfasi_soup = BeautifulSoup(iddaa_html_adress, "lxml")
                # iddaa disabletse geç , 50 den fazla arka arkaya disable olayı olmussa sayfayı degistir
                if iddaa_sayfasi_soup.find('a',
                                           class_="widget-match-detail-submenu__icon widget-match-detail-submenu__icon--iddaa   widget-match-detail-submenu__icon--disabled  ") != None:
                    gecilen_mac += 1
                    print(str(gecilen_mac), mac_ismi)
                    if gecilen_mac > 30:
                        break
                    continue

                for data_id in list(iddaa_kodlari):
                    aranan = None
                    if data_id == '18':
                        ustler = iddaa_sayfasi_soup.find_all("li", {"data-market": data_id})
                        for ust in ustler:
                            if ust.find("span", class_="widget-iddaa-markets__header-text").text == " 2,5 Alt/Üst ":
                                aranan = ust
                                break
                    else:
                        aranan = iddaa_sayfasi_soup.find("li", {"data-market": data_id})
                    if aranan == None:
                        istenen_yok = True
                        break
                    icerik_sayisi = len(aranan.find_all('a', class_="widget-iddaa-markets__link"))
                    if icerik_sayisi != iddaa_kodlari[data_id]:
                        istenen_yok = True
                        break
                if istenen_yok == True:
                    gecilen_mac += 1
                    print(str(gecilen_mac), mac_ismi)
                    if gecilen_mac > 30:
                        break
                    continue
                else:
                    gecilen_mac = 0
                print(mac_ismi)
                containers = iddaa_sayfasi_soup.find_all('li', class_="widget-iddaa-markets__market-item")
                try:
                    ev_skor = int(
                        iddaa_sayfasi_soup.find("span", class_="p0c-soccer-match-details-header__score-home").text)
                    dep_skor = int(
                        iddaa_sayfasi_soup.find("span", class_="p0c-soccer-match-details-header__score-away").text)
                    iy_sonucu = iddaa_sayfasi_soup.find("div",
                                                        class_="p0c-soccer-match-details-header__detailed-score").text
                    iy_ev = int(iy_sonucu[5])
                    iy_dep = int(iy_sonucu[9])
                except ValueError:
                    continue
                except AttributeError:
                    continue

                mac_oran_listesi = []
                label_satirla(id, iy_ev, iy_dep, ev_skor, dep_skor)
                query = "INSERT INTO tbl_maclar values(" + str(id) + "," + "'{}'".format(mac_ismi) + "," + str(
                    iy_ev) + "," + str(iy_dep) + "," + str(ev_skor) + "," + str(dep_skor)
                for container in containers:
                    data_kodu = container.get('data-market')

                    iddaa_icerikleri = container.find_all('a', class_="widget-iddaa-markets__link")
                    if data_kodu in list(iddaa_kodlari):
                        if data_kodu == '18':
                            if container.find("span",
                                              class_="widget-iddaa-markets__header-text").text != " 2,5 Alt/Üst ":
                                continue
                        for iddaa_icerigi in iddaa_icerikleri:
                            try:
                                value = float(iddaa_icerigi.find("span", class_="widget-iddaa-markets__value").contents[
                                                  0].strip())
                            except:
                                value = 'NULL'
                            query += "," + str(value)

                query += ")"
                print(query)
                cur = mydb.cursor()
                cur.execute(query)
                mydb.commit()
                cur.close()
                id += 1

            date = date - datetime.timedelta(days=1)
        # maclarin_oranlari_listesi.append([day,mac_oran_listesi])
        driver.close()
        mydb.close()
    except ConnectionAbortedError:
        date = date - datetime.timedelta(days=1)
        driver.close()
        mydb.close()
        with open("ID.txt", 'w', encoding='utf-8') as f:
            f.write(str(id))
