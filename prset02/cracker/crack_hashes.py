#! /usr/bin/env python
import string
import sys
import crypt
from passlib.hash import des_crypt
import logging


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='crackapp.log',
                    filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)

formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)







usernames_list = ["chattan.armani","michel.lowell","croft.blumstein","wolf.berg","stuart.sadler","gibson.clinton","derrick.potter","berg.albini","clay.meindl","whitaker.gorman","coupe.pickering","burnham.rinne","dupont.mackay","lawson.gerber","henry.giordana","bilbao.washington","burnham.huxtable","favre.rose","samuel.kelley","heath.robertson","hauer.noel","charteris.rogers","sniders.saller","kuntz.michael","kistner.landau","parker.mueller","victor.riddell","glover.zubiaga","sims.butler","durant.tuft","oleary.graner","conti.wieck","foss.sauber","salomon.conti","grunewald.barclay","morin.dolan","lehrer.wilson","garland.quickley","acerbi.torres","cooney.bohn","hamilton.nielson","benton.sutton","stroud.richard","smalls.mathers","wickham.endicott","roydon.power","livingstone.coburn","miner.harper","morgenstern.mullen","russell.brandon","clay.schermer","grierson.geissler","adessi.cole","thompson.vincent","berry.hilton","abram.drummond","dahl.cooke","forbes.goodwin","barron.reiher","beake.sauber","papp.hartmann","ferguson.everett","davies.moser","brown.segal","horton.oberst","keen.nathanson","dudley.mcmullen","cline.cumming","roscoe.philips","viteri.powers","sauber.wyndham","freeman.akins","albero.bertrand","pierson.terrell","geary.wolfe","polin.hofmeister","carver.abel","bates.bagley","cavey.washington","denman.garza","kroger.daviau","gross.bertrand","brown.newell","bruce.wembley","gilliam.fox","aravena.bennett","dennell.patton","delany.carmichael","mandel.douglas","buchanan.dudley","sampson.dubois","macnab.paquet","garner.lehmann","landau.prescott","albert.daniel","guinness.gehrig","bryson.macneil","groos.pearce","schmidt.irving","bureau.lorenz","admin"]

passwords_list =  ["q64c3EgXdCVPo",\
"vI6sCN0uqzSZk",\
"uKu8ZKbdKmcVs",\
"RYdeL0HUwTqrc",\
"xtIN65.PgwBNg",\
"z0.lu3I7.zsl.",\
"2CBmLNOIVz/sE",\
"nk922vyqlwZIY",\
"mEOGOpIGbLuzo",\
"K2xtAuXU8xXw.",\
"tZcBVe6iRXA/o",\
"WpNE7IzeaPKrA",\
"kvZTGCQiB3WFM",\
"XfjyWkpjJQKoQ",\
"bxwrg2jUNOyLg",\
"E7WHSW1rR74PM",\
"SlE1Xo2Upy1dc",\
"oKlyCHRFTa8UM",\
"2uaKIrwpeFqM6",\
"S4hXH6d15ov36",\
"Z7zErdUSQ5EZQ",\
"Y.02DbSXE6B/Y",\
"0NCe09Teag.og",\
"cAxjN3eCEILbc",\
"eWipkFCFNDQD6",\
"ayCS2ZklJcAsg",\
"8YoQ5SISVTiKc",\
"5zjMiaVtRI876",\
"LGqjApJm1i5fU",\
"46sdF15G7.z7o",\
"41p9vEU4A/f1Y",\
"gYUdQYwu3sE0U",\
"YJDzgMeezcVP2",\
"nvp9AFbtkAcZE",\
"DpWFNNpcRLnq6",\
"mfkM2rNzhj3aM",\
"gdgO8L.A7RULs",\
"EffNwKWkugduI",\
"/cqh0IdPoJVT.",\
"NCrDWc.7KB5Xg",\
"eRpIhwQX5.sBk",\
"mWnhrDZRQOhdI",\
"f886UyJYtIYyM",\
"NJGvtdRT0zM.A",\
"4OUZF.qQsvxDA",\
"ISryzI/DobiJY",\
"H25RadRzpijLI",\
"ArduBWaHz9SrA",\
"IYz23XQvxVevs",\
"XQIH/TBNW3rq6",\
"c5h618TbzuSEc",\
"fJBIAlOEjkMSo",\
"/Hf.a.x35009g",\
"doTCB1QEl7NNU",\
"n5HpLmHheDNRA",\
"/lW4219RDkWMg",\
"lyOQCIVD0WDcM",\
"pZ8cNCXetd4TA",\
"IiJ6urvLUo6yQ",\
"oVWuALEsOrFvM",\
"DJiqfysFsSIRw",\
"dq2qTKpohLURU",\
"rTdIT6klZ.zM2",\
"VqO6po/ALVkaI",\
"dUW4ZgsZW1T56",\
"CTYQ0zH2EaK6o",\
"0DLizaz/XTcQI",\
"6Xf0xaNeRPRYo",\
"QRjBf2hFZOBmI",\
"xANpncmfnyY2A",\
"GARw7qseu9GQM",\
"bMRBLYbZCPhLI",\
"kf57gNxWvxmWQ",\
"yHc2ISSMhcDf2",\
"ss0Bf8FRZgAsg",\
"wVnQ4GGBrOiBY",\
"g4sCkuv.srpcQ",\
"WTzZv9yAEaot.",\
"98vuJTvvMVgLo",\
"RaOpj3aIhEWVY",\
"JUzK1rpHZ6RnE",\
"M/SaLm1Wj1J9U",\
"AgzSRTpr65bsQ",\
"WLkAzixIxJ8lM",\
"x2muHCTPNjREM",\
"TyLPvCTG/uRNs",\
"/fK2xuPs99O.Q",\
"iiZZgw40VSJTo",\
"22nWQ9Q2PmQRU",\
"ZAkY4GJIl/ToY",\
"P0IM6kCsnAmgE",\
"LlbtCmEpkjOCg",\
"dV3kVQcbU5D0c",\
"ADivEfeyzzKZg",\
"MEwZAyjkc.rxQ",\
"VFOlmfYsaqPDY",\
"Yaymz96pGLiDk",\
"Ty3ImRLkEmi6M",\
"6lBibHDimrEdk",\
"7rCLcR88tD5CU",\
"CEBOi08g9JhT."]


# prev, I used  these vars. What's intereesting is, that I found a lot of hashing collisions! so I created a found array just for curiousity how many hit a collision. 
hash = ""
found = []
# but now I just used for loop over all the (usernames,hashes) and call that bruteforce function




def bruteforce(username, hash):
	# string.printable:
	#     0-9   Numbers
	#     10-35 Small
	#     36-61 Caps
	i_num = 0
	i_sm = 10
	i_cap = 36
	list = string.printable
	
	# Regex:  ?[two caps][two smalls][two numbers]!
	# found during first test: ?MZmn57!
	password =""
	start = False
	for c1 in range(i_cap, i_cap+26):
		for c2 in range(i_cap, i_cap+26):
			for c3 in range(i_sm, i_sm+26):
				for c4 in range(i_sm, i_sm+26):
					#print password
					for c5 in range(i_num, i_num+10):
						for c6 in range(i_num, i_num+10):
							#if start == False:
								#start = True
								#c1=list.index('M')
								#c2=list.index('Z')
								#c3=list.index('m')
								#c4=list.index('n')	
								#c5=list.index('5')
								#c6=list.index('6')
							c_cap1 = list[c1]
							c_cap2 = list[c2]
							c_sm1  = list[c3]	
							c_sm2  = list[c4]	
							c_num1 = list[c5]
							c_num2 = list[c6]
							password = ('?' + c_cap1 + c_cap2 + c_sm1 + c_sm2 + c_num1 + c_num2 + '!')
							#print password
							#test_hash = des_crypt.encrypt(password)
							#print test_hash
							if des_crypt.verify(password, hash):
								logging.info("{\"username\":\"" + username + "\", \"password\":" + "\""+password+"\"}")
								return
								#exit(0)


logging.info( "Len of usernames ="+str(len(usernames_list)))
logging.info( "Len of passwords = "+str(len(passwords_list)))
for i in range(len(passwords_list)):
        logging.info( "Now trying:" + passwords_list[i] + ", for user:"+usernames_list[i])
        bruteforce(usernames_list[i],passwords_list[i])

