import csv
import toml
import os

def health_function(_type, _smell , _cm, rows, switch_cs_data):
   print (switch_cs_data)
   if 'Ratio' in _smell: #For ratio measures , multiply by 100 and use float type
     _cm = float(_cm) * 100
   elif _cm == '-':
      return 0
   else:
     _cm = int(_cm)
   rw = 100
   #health, Small Code Smell, Large Code Smell
   h = scs = lcs = 0.00
   #Weigth Small Code Smell, Weight Large Code Smell
   wt_scs = wt_lcs = 1

   #Check the type (Class or Method)
   if _type == "class":
      if _smell == "Lines of Code":
          scs_list = switch_cs_data.get(_type).get('SmallClass')
          scs = scs_list[0]
          wt_scs = scs_list[1]

          lcs_list = switch_cs_data.get(_type).get('LargeClass')
          lcs = lcs_list[0]
          wt_lcs = lcs_list [1]

          rows["loc"] = rows["loc"] + 1
      elif _smell == "Comment-to-Code Ratio":
          scs_list = switch_cs_data.get('comments').get('CommentsToCodeRationLower')
          scs = scs_list[0] * 100
          wt_scs = scs_list[1] * 100

          lcs_list = switch_cs_data.get('comments').get('CommentsToCodeRationUpper')
          lcs = lcs_list[0] * 100
          wt_lcs = lcs_list [1] * 100

          rows["ctcr"] = rows["ctcr"] + 1
      elif _smell == "Number of Outgoing Invocations": #GOD class for Classes
          lcs_list = switch_cs_data.get(_type).get('GodClass')
          lcs = lcs_list[0]
          wt_lcs = lcs_list [1]

          rows["godc"] = rows["godc"] + 1
      elif _smell == "Number of Directly-Used Elements": #InappropiateIntimacy for Classes
          lcs_list = switch_cs_data.get(_type).get('InappropriateIntimacy')
          lcs = lcs_list[0]
          wt_lcs = lcs_list [1]

          rows["inai"] = rows["inai"] + 1
      elif _smell == "Number of Parameters":
         return 0
      else:
         return 0

   elif _type == "method":
      if _smell == "Lines of Code":
          scs_list = switch_cs_data.get(_type).get('SmallMethod')
          scs = scs_list[0]
          wt_scs = scs_list[1]

          lcs_list = switch_cs_data.get(_type).get('LargeMethod')
          lcs = lcs_list[0]
          wt_lcs = lcs_list [1]

          rows["loc"] = rows["loc"] + 1
      elif _smell == "Comment-to-Code Ratio":
          scs_list = switch_cs_data.get('comments').get('CommentsToCodeRationLower')
          scs = scs_list[0] * 100
          wt_scs = scs_list[1] * 100

          lcs_list = switch_cs_data.get('comments').get('CommentsToCodeRationUpper')
          lcs = lcs_list[0] * 100
          wt_lcs = lcs_list [1] * 100

          rows["ctcr"] = rows["ctcr"] + 1
      elif _smell == "Number of Outgoing Invocations": #NO GOD class for Methods
          return 0
      elif _smell == "Number of Directly-Used Elements":   #NO InappropiateIntimacy for Methods
          return 0
      elif _smell == "Number of Parameters":
          lcs_list = switch_cs_data.get(_type).get('LargeParameterList')
          lcs = lcs_list[0]
          wt_lcs = lcs_list [1]

          rows["nop"] = rows["nop"] + 1
      else:
          return 0

   scs = scs * wt_scs # Multiply Code Smell by Weight
   lcs = lcs * wt_lcs # Multiply Code Smell by Weight
   if _cm < scs: #Condition for penalization when code metric is under small Code Smell (cm < scm)
     h = rw - ((_cm - scs)**2) / (scs**2) * rw
     return h
   elif _cm <= lcs:
     h = rw
     return h
   else: #Condition for penalization when code metric is over large Code Smell (cm > lcs)
     h = rw - ((_cm - lcs)**2) / (lcs**2) * rw
     if h < 0:
       h = 0
     return h

def calculate_health(toml_config, csv_path):
   #print (csv_path + "metrics.csv")
   #if os.path.exists(csv_path + "metrics.csv"):
   if os.path.exists(csv_path):
       #with open(csv_path + 'metrics.csv', newline='') as csvfile:
       with open(csv_path, newline='') as csvfile:
            #Using Dict Reader
          reader = csv.DictReader(csvfile)
          lines = 0
          _headers =  [
             'Type of Smell',
             'Lines of Code',
             'Comment-to-Code Ratio',
             'Number of Outgoing Invocations', #GOD class for Classes
             'Number of Directly-Used Elements', #InappropiateIntimacy for Classes
             'Number of Parameters'
             ]

          h = {"loc": 0, "ctcr": 0.00, "godc": 0, "inai": 0,"nop": 0}
          rows = {"loc": 0, "ctcr": 0, "godc": 0, "inai": 0, "nop": 0}
          avg = {"loc": 0.00, "ctcr": 0.00, "godc": 0, "inai": 0, "nop": 0.00}

          for row in reader:
             h["loc"] = h["loc"] + health_function(row[_headers[0]].lower(), _headers[1], row[_headers[1]],rows, toml_config)
             h["ctcr"] = h["ctcr"] + health_function(row[_headers[0]].lower(), _headers[2], row[_headers[2]],rows, toml_config)
             h["godc"] = h["godc"] + health_function(row[_headers[0]].lower(), _headers[3], row[_headers[3]],rows, toml_config)
             h["inai"] = h["inai"] + health_function(row[_headers[0]].lower(), _headers[4], row[_headers[4]],rows, toml_config)
             h["nop"] = h["nop"] + health_function(row[_headers[0]].lower(), _headers[5], row[_headers[5]],rows, toml_config)

             lines = lines +1
       #print(lines)

       avg["loc"] = h["loc"]/rows["loc"]
       avg["ctcr"] = h["ctcr"]/rows["ctcr"]
       avg["godc"] = h["godc"]/rows["godc"]
       avg["inai"] = h["inai"]/rows["inai"]
       avg["nop"] = h["nop"]/rows["nop"]

       # print(avg["loc"])
       # print(avg["ctcr"])
       # print(avg["godc"])
       # print(avg["inai"])
       # print(avg["nop"])
       total = (avg["loc"] + avg["ctcr"] + avg["nop"] + avg["godc"] + avg["inai"]) / 5
       return total
   else:
        return "File not found"

# switch_cs_data = code_smell.code_smells()
# DEFAULT_PATH = 'C:\\Users\\hecto\\OneDrive\\Documents\\Software Practicum\\HealthCode\\'
# healthTotal = calculateHealth(DEFAULT_PATH)
# print("----TOTAL HEALTH-------:")
# print (healthTotal)
