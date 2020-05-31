# matsui
API for Matsui 松井証券

#Example
```
from matsui import matsui_api

financeobj = matsui_api.matsui()
result = financeobj.login('12341212', 'f1234567')
financeobj.token('trade4321')
print(financeobj.sell('1306', '10', '1,750'))
```
