import re


txt = "Shkolla Digjitale Prizren"
x = re.search("^S.*Pri.*n$", txt)
 
if x:
  print("YES! We have a match!")
else:
  print("No match")
  
# []	A set of characters	"[a-m]"	
# \	Signals a special sequence (can also be used to escape special characters)	"\d"	
# .	Any character (except newline character)	"he..o"	
# ^	Starts with	"^hello"	
# $	Ends with	"planet$"	
# *	Zero or more occurrences	"he.*o"	
# +	One or more occurrences	"he.+o"	
# ?	Zero or one occurrences	"he.?o"	
# {}	Exactly the specified number of occurrences	"he.{2}o"	
# |	Either or	"falls|stays"	
# ()	Capture and group

#findall
print("\nFindAll")
txt = "Shkolla Digjitale Prizren"
x = re.findall("l", txt)
print(x)

#search
print("\nSearch")
x = re.search("\s", txt)

print("The first white-space character is located in position:", x.start())

x = re.search("Prizren", txt)
print(x)
print(x.start())

#split
print("\n Split")
x = re.split("\s", txt)
print(x)


#Sub
print("/n Sub")
x = re.sub("\s", " ", txt)
print(x)

#Span
print("/n Span")
x = re.search(r"\bD\w+", txt)
print(x.span())