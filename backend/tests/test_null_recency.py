"""Exercise real service methods without Firebase initialization or network access."""
import ast,asyncio,logging,unittest
from datetime import datetime,timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import Any,Dict,List,Optional
ROOT=Path(__file__).resolve().parents[1] / 'src' / 'services'
def load(name,klass):
 tree=ast.parse((ROOT/name).read_text());node=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==klass)
 ns=dict(db=None,datetime=datetime,timedelta=timedelta,Dict=Dict,List=List,Optional=Optional,Any=Any,logger=logging.getLogger('test'))
 exec(compile(ast.Module(body=[node],type_ignores=[]),str(ROOT/name),'exec'),ns);return ns[klass]()
def attach(service,items):
 docs=[SimpleNamespace(id=str(i),to_dict=lambda value=row:value) for i,row in enumerate(items)]
 service.db=SimpleNamespace(collection=lambda _:SimpleNamespace(where=lambda *args:SimpleNamespace(stream=lambda:docs)));return service
class RecencyTests(unittest.TestCase):
 def rows(self):
  now=datetime.now().timestamp()*1000
  return [{'lastWorn':None,'wearCount':0},{'wearCount':0},{'lastWorn':0,'wearCount':0},{'lastWorn':now,'wearCount':1},{'lastWorn':now-240*86400000,'wearCount':4}]
 def test_utilization_counts_null_as_never_worn_without_discarding_real_recent_wears(self):
  service=attach(load('utilization_service.py','UtilizationService'),self.rows());value=asyncio.run(service.calculate_utilization_percentage('owner'))
  self.assertNotIn('error',value);self.assertEqual((value['total_items'],value['items_worn'],value['dormant_items'],value['utilization_percentage']),(5,1,4,20.0))
 def test_dormant_list_includes_never_worn_and_old_item(self):
  service=attach(load('utilization_service.py','UtilizationService'),self.rows());value=asyncio.run(service.get_dormant_items('owner'))
  self.assertEqual(len(value),4);self.assertEqual(sum(x['days_since_worn']==999 for x in value),3)
 def test_revived_score_uses_real_ratio_instead_of_fallback_half(self):
  service=attach(load('gws_service.py','GWSService'),self.rows());value=asyncio.run(service._calculate_revived_items_score('owner'));self.assertEqual(value,0.2)
 def test_all_never_worn_score_is_zero(self):
  service=attach(load('gws_service.py','GWSService'),[{'lastWorn':None,'wearCount':0}]);self.assertEqual(asyncio.run(service._calculate_revived_items_score('owner')),0)
if __name__=='__main__':unittest.main()
