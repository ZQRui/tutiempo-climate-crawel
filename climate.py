
import requests
from bs4 import BeautifulSoup
import argparse
import logging
import os

argp=argparse.ArgumentParser()
argp.add_argument("year",type=int)
argp.add_argument("month",type=int)
argp.add_argument("place_id",type=str)

se=requests.Session()
# se.proxies=proxies
se.headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
            ,"Origin":"https://en.tutiempo.net"
            ,"Content-Type":"application/x-www-form-urlencoded"}

def get_weather(year,month,place_id="548230"):
    logging.info("start get climate from place id: {place_id} year:{year} month:{month} ".format(place_id=place_id,year=year,month=month))
    url="https://en.tutiempo.net/climate/{month:02}-{year:04}/ws-{place_id}.html".format(year=year,month=month,place_id=place_id)
    result=se.get(url)
    b1=BeautifulSoup(result.content,"html.parser")
    form=b1.select("div.DivInfoAbuso form input")
    data=dict([(form[i].attrs["name"],form[i].attrs["value"]) for i in (0,1)])
    send_data="&".join(["{}={}".format(k,v) for k,v in data.items()])
    logging.debug("get taenc ok")
    result2=se.post(url,data=send_data)
    b2=BeautifulSoup(result2.content,"html.parser")
    trs=b2.select(".mt5.minoverflow.tablancpy table tr")
    table=[[th.text for th in trs[0].select("th")],]+[[td.text.replace('\xa0','') for td in tr] for tr in trs[1:-2]]
    logging.debug("get climate table ok")
    write_data="\n".join([",".join(tr)for tr in table])
    logging.debug(write_data)
    data_dir="climate-data"
    if os.path.isdir(data_dir):
        os.mkdir(data_dir)
    
    fname="{place_id}-{year:04}-{month:02}.csv".format(year=year,month=month,place_id=place_id)
    fpath=os.path.join(data_dir,fname)
    with open(fpath,"w") as fp:
        fp.write(write_data)
    logging.info("Get climate data done, save in file: {}".format(fpath))

if __name__=="__main__":
    logging.basicConfig(level=logging.DEBUG)
    args=argp.parse_args()
    get_weather(args.year,args.month,args.place_id)
