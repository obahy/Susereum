import csv
import toml
import os

def health_function(_type, _smell , _cm, rows, switch_cs_data):
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
         
      elif _smell == "Comment-to-Code Ratio":                
          scs_list = switch_cs_data.get('comments').get('CommentsToCodeRatioLower')
          scs = scs_list[0] * 100
          wt_scs = scs_list[1] * 100

          lcs_list = switch_cs_data.get('comments').get('CommentsToCodeRatioUpper')
          lcs = lcs_list[0] * 100
          wt_lcs = lcs_list [1] * 100
        
      elif _smell == "Number of Outgoing Invocations": #GOD class for Classes
          lcs_list = switch_cs_data.get(_type).get('GodClass')
          lcs = lcs_list[0]
          wt_lcs = lcs_list [1]
      
      elif _smell == "Number of Directly-Used Elements": #InappropiateIntimacy for Classes
          lcs_list = switch_cs_data.get(_type).get('InappropriateIntimacy')
          lcs = lcs_list[0]
          wt_lcs = lcs_list [1]

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

      elif _smell == "Comment-to-Code Ratio":      
          scs_list = switch_cs_data.get('comments').get('CommentsToCodeRatioLower')
          scs = scs_list[0] * 100
          wt_scs = scs_list[1] * 100

          lcs_list = switch_cs_data.get('comments').get('CommentsToCodeRatioUpper')
          lcs = lcs_list[0] * 100
          wt_lcs = lcs_list [1] * 100

      elif _smell == "Number of Outgoing Invocations": #NO GOD class for Methods
          return 0
      elif _smell == "Number of Directly-Used Elements":   #NO InappropiateIntimacy for Methods
          return 0
      elif _smell == "Number of Parameters":          
          lcs_list = switch_cs_data.get(_type).get('LargeParameterList')
          lcs = lcs_list[0]
          wt_lcs = lcs_list [1]

      else:
          return 0

   rows[_smell] = rows[_smell] + 1 # Row counter per type of smell
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

def calculate_health(sus_config, codeAnalysis_path):
   if os.path.exists(codeAnalysis_path):          
       with open(codeAnalysis_path, newline='') as csvfile:
         # Using csv Reader 
         reader = csv.reader(csvfile)
         # CSV Header list:  
         # 0: Type of Smell, 1: Name, 2: Lines of Code, 3: Comment-to-Code Ratio
         # 4: Number of Directly-Used Elements, 5: Number of Outgoing Invocations
         # 6: Name of Owner Class, 7: Number of Parameters
         head = next(reader)
         # h is a DD with the necessary Header to count returned by health_function
         h = {head[2]: 0, head[3]: 0.00, head[5]: 0, head[4]: 0,head[7]: 0}
         rows = {head[2]: 0, head[3]: 0, head[5]: 0, head[4]: 0, head[7]: 0}
         avg = {head[2]: 0.00, head[3]: 0.00, head[5]: 0, head[4]: 0, head[7]: 0.00}
         print (rows[head[2]])
         lines = 0
         for x in reader:
             h[head[2]] = h[head[2]] + health_function(x[0].lower(), head[2], x[2], rows, sus_config)
             h[head[3]] = h[head[3]] + health_function(x[0].lower(), head[3], x[3], rows, sus_config)
             h[head[4]] = h[head[4]] + health_function(x[0].lower(), head[4], x[4], rows, sus_config)
             h[head[5]] = h[head[5]] + health_function(x[0].lower(), head[5], x[5], rows, sus_config)
             h[head[7]] = h[head[7]] + health_function(x[0].lower(), head[7], x[7], rows, sus_config)
             lines = lines +1
       avg[head[2]] = h[head[2]]/rows[head[2]]
       avg[head[3]] = h[head[3]]/rows[head[3]]
       avg[head[5]] = h[head[5]]/rows[head[5]]
       avg[head[4]] = h[head[4]]/rows[head[4]]
       avg[head[7]] = h[head[7]]/rows[head[7]]
     
    #    print(avg[head[2]])
    #    print(avg[head[3]])
    #    print(avg[head[5]])
    #    print(avg[head[4]])
    #    print(avg[head[7]])
       total = (avg[head[2]] + avg[head[3]] + avg[head[5]] + avg[head[4]] + avg[head[7]]) / 5
       return total
   else:
       print("File not found")
       return (0)  

#switch_cs_data = code_smell.code_smells()
#witch_cs_data example
# {'class': 
#     {'LargeClass': [200, 1], 
#      'SmallClass': [100, 1], 
#      'GodClass': [5, 1], 
#      'InappropriateIntimacy': [2, 1]}, 
#  'method': 
#     {'LargeMethod': [10, 1], 
#      'SmallMethod': [3, 1], 
#      'LargeParameterList': [4, 1]}, 
#  'comments': 
#     {'CommentsToCodeRatioLower': [0.2, 0.01], 
#      'CommentsToCodeRatioUpper': [0.5, 0.01]}
# }

# DEFAULT_PATH = 'C:\\Users\\hecto\\OneDrive\\Documents\\Software Practicum\\HealthCode\\'
# healthTotal = calculateHealth(DEFAULT_PATH)
# print("----TOTAL HEALTH-------:")
# print (healthTotal)