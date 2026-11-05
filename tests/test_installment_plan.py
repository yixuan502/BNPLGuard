from decimal import Decimal
import pytest
from src.installment_plan import calculate_plan

@pytest.mark.parametrize("p,u,n,regular,last",[(600,0,3,"200","200"),(600,150,3,"150","150"),(100,0,3,"33.33","33.34"),(0,0,3,"0","0"),(100,100,3,"0","0")])
def test_allocation(p,u,n,regular,last):
    a=calculate_plan(p,u,n)
    assert a['regular']==Decimal(regular) and a['final']==Decimal(last)
    assert a['regular']*(n-1)+a['final']==a['remaining']
    assert a['maximum']==max(a['regular'],a['final'])

@pytest.mark.parametrize("p,u,n",[(-1,0,3),(1,2,3),(float('nan'),0,3),(float('inf'),0,3),('2',0,3),(1.001,0,3),(1,0,0),(1,0,1.5),(1,0,True)])
def test_invalid(p,u,n):
    with pytest.raises(ValueError): calculate_plan(p,u,n)
