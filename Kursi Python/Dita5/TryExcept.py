
  

try:
  f = open("demofile.txt", "w")
  try:
    f.write("Arianit Tershnjaku")
  except:
    print("Something went wrong when writing to the file")
  finally:
    f.close()
except:
  print("Something went wrong when opening the file")