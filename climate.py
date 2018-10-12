
import requests
from bs4 import BeautifulSoup
import argparse
import logging
import os


se=requests.Session()
# se.proxies=proxies
se.headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
            ,"Origin":"https://en.tutiempo.net"
            ,"Content-Type":"application/x-www-form-urlencoded"}

def get_weather(year,month,place_id="548230"):
    logging.info("start get climate from place id: {place_id} year:{year} month:{month} ".format(place_id=place_id,year=year,month=month))
    url="https://en.tutiempo.net/climate/{month:02}-{year:04}/ws-{place_id}.html".format(year=year,month=month,place_id=place_id)
    result=se.get(url)
    if result.status_code==404:
        logging.error("place id error {}".format(place_id))
        exit()
        return
    b1=BeautifulSoup(result.content,"html.parser")
    form=b1.select("div.DivInfoAbuso form input")
    data=dict([(form[i].attrs["name"],form[i].attrs["value"]) for i in (0,1)])
    send_data="&".join(["{}={}".format(k,v) for k,v in data.items()])
    logging.debug("get taenc ok")
    result2=se.post(url,data=send_data)
    if result2.status_code==404:
        logging.error("climate data of: palce {} year {} month{} not exist".format(place_id,year,month))
        return 
    b2=BeautifulSoup(result2.content,"html.parser")
    se.close()
    trs=b2.select(".mt5.minoverflow.tablancpy table tr")
    table=[[th.text for th in trs[0].select("th")],]+[[td.text.replace('\xa0','') for td in tr] for tr in trs[1:-2]]
    logging.debug("get climate table ok")
    write_data="\n".join([",".join(tr)for tr in table])
    logging.debug(write_data)
    data_dir="climate-data"
    if not os.path.isdir(data_dir):
        os.mkdir(data_dir)
    fname="{place_id}-{year:04}-{month:02}.csv".format(year=year,month=month,place_id=place_id)
    fpath=os.path.join(data_dir,fname)
    with open(fpath,"w") as fp:
        fp.write(write_data)
    logging.info("Get climate data done, save in file: {}".format(fpath))

argp=argparse.ArgumentParser()
argp.add_argument("place_id",type=str)
argp.add_argument("start_year",type=int)
argp.add_argument("start_month",type=int)
argp.add_argument("end_year",type=int,default=None)
argp.add_argument("end_month",type=int,default=None)

if __name__=="__main__":
    logging.basicConfig(level=logging.INFO,format = '%(asctime)s  %(filename)s : %(levelname)s  %(message)s', datefmt  = '%Y-%m-%d %A %H:%M:%S')
    logging_file_handler=logging.FileHandler("climate-crawel.log", mode="a")
    logging_file_handler.setLevel(logging.DEBUG)
    logging.getLogger().addHandler(logging_file_handler)
    args=argp.parse_args()
    if not (args.end_year and args.end_month):
        get_weather(args.start_year,args.start_month,args.place_id)
    else:
        sy=args.start_year
        sm=args.start_month
        ey=args.end_year
        em=args.end_month
        if ey<sy:
            logging.error("must be end > start")
        elif ey==sy:
            if sm<em:
                logging.error("must be end > start")
            else:
                for m in range(sm,em):
                    get_weather(sy,m,args.place_id)
        else:
            for m in range(sm,13):
                get_weather(sy,m,args.place_id)
            for y in range(sy+1,ey):
                for m in range(1,13):
                    get_weather(y,m,args.place_id)
            for m in range(1,em+1):
                get_weather(ey,m,args.place_id)

        
