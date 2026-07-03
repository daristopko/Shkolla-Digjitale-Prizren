"""
Çka është datetime?

datetime në Python përdoret për:
- me punu me data (date)
- me punu me kohë (time)
- me marrë datën dhe kohën aktuale
- me llogarit diferenca mes datave
datetime = punon me data dhe kohë
now() = jep momentin aktual
date() = vetëm data
time() = vetëm ora
strftime() = formatim i bukur
"""

#DATA DHE KOHA AKTUALE

import datetime

# data dhe koha aktuale
now = datetime.datetime.now()

print("Data dhe koha aktuale:")
print(now)

#VETËM DATA
today = datetime.date.today()
print("\nData aktuale:") #\n = new line (rreshtim i ri)
print(today)

#KRIJIM I DATA-S MANUALISHT
# krijim i data-s manualisht

my_birthday = datetime.date(1996, 4, 2) #(viti, muaji, dita)
print("\nData e ditëlindjes sime:")
print(my_birthday)

#KRIJIM I KOHËS

t = datetime.time(14, 30, 0) #(ora, minuta, sekonda)

print("Koha:")
print(t)

#FORMATO DATA (më e lexueshme)
now = datetime.datetime.now()

print(now.strftime("%d-%m-%Y")) # %d = dita, %m = muaji, %Y = viti (4 shifra)
print(now.strftime("%H:%M:%S"))  # %H = ora (24h), %M = minuta, %S = sekonda
 
#DATA + KOHA BASHKË
dt = datetime.datetime(2026, 5, 27, 14, 30) #(viti, muaji, dita, ora, minuta)

print("Data dhe koha:")
print(dt)

# %a	Weekday, short version	Wed	
# %A	Weekday, full version	Wednesday	
# %w	Weekday as a number 0-6, 0 is Sunday	3	
# %d	Day of month 01-31	31	
# %b	Month name, short version	Dec	
# %B	Month name, full version	December	
# %m	Month as a number 01-12	12	
# %y	Year, short version, without century	18	
# %Y	Year, full version	2018	
# %H	Hour 00-23	17	
# %I	Hour 00-12	05	
# %p	AM/PM	PM	
# %M	Minute 00-59	41	
# %S	Second 00-59	08	
# %f	Microsecond 000000-999999	548513	
# %z	UTC offset	+0100	
# %Z	Timezone	CST	
# %j	Day number of year 001-366	365	
# %U	Week number of year, Sunday as the first day of week, 00-53	52	
# %W	Week number of year, Monday as the first day of week, 00-53	52	
# %c	Local version of date and time	Mon Dec 31 17:41:00 2018	
# %C	Century	20	
# %x	Local version of date	12/31/18	
# %X	Local version of time	17:41:00	
# %%	A % character	%	
# %G	ISO 8601 year	2018	
# %u	ISO 8601 weekday (1-7)	1	
# %V	ISO 8601 weeknumber (01-53)	01
