"""Optional bounded rewrite adapter; no provider client, keys, network or live calls."""
from dataclasses import dataclass
from copy import deepcopy
from queue import Queue,Empty
from threading import Thread
from math import isfinite

@dataclass(frozen=True)
class RewriteOptions:
    enabled:bool=False
    cost_authorized:bool=False
    financial_data_transfer_authorized:bool=False
    timeout_seconds:float=3.0
    provider_configured:bool=False
    def __post_init__(self):
        if not isinstance(self.timeout_seconds,(int,float)) or not isfinite(self.timeout_seconds) or self.timeout_seconds<=0:raise ValueError('Positive finite timeout required')
        if any(type(x) is not bool for x in [self.enabled,self.cost_authorized,self.financial_data_transfer_authorized,self.provider_configured]):raise ValueError('Explicit boolean authorization flags required')

class OptionalLLMAdapter:
    """An injected transport may choose approved phrasing/order; it cannot edit facts.

    Provider integration is deliberately not configured. Enabling requires specific
    cost and financial-data-transfer authorization. A transport must honor the
    passed timeout; daemon isolation bounds UI waiting but cannot cancel a remote
    request already sent. Arbitrary generated prose is rejected, not semantically
    certified by a numeric-only validator.
    """
    def __init__(self,options=None,transport=None):self.options=options or RewriteOptions();self.transport=transport

    def rewrite(self,segments,digest):
        default=[{'id':s['id'],'variant':0} for s in segments];o=self.options
        if not o.enabled:return default,'disabled',None
        if not(o.cost_authorized and o.financial_data_transfer_authorized):return default,'fallback','Specific cost and financial-data transfer authorization missing; no transport called'
        if not o.provider_configured or self.transport is None:return default,'fallback','No provider/transport configured; no transport called'
        request={'schema_version':'approved-phrasing-v1','facts_digest':digest,'segments':deepcopy(segments),
                 'instruction':'Return exactly facts_digest and choices. choices must contain each segment id once and an existing integer variant index. No free text, new numbers, advice or omitted limitations.'}
        queue=Queue(maxsize=1)
        def call():
            try:queue.put(('ok',self.transport(request,timeout_seconds=o.timeout_seconds)))
            except Exception:queue.put(('error',None))
        Thread(target=call,daemon=True).start()
        try:state,response=queue.get(timeout=o.timeout_seconds)
        except Empty:return default,'fallback','Rewrite timed out; original template retained'
        if state!='ok':return default,'fallback','Rewrite transport failed; original template retained'
        if not self._valid(response,segments,digest):return default,'fallback','Rewrite validation failed; factual or numeric edits are not accepted'
        return response['choices'],'validated','Only approved phrasing/order selected; no factual edits permitted'

    @staticmethod
    def _valid(response,segments,digest):
        if not isinstance(response,dict) or set(response)!={'facts_digest','choices'} or response['facts_digest']!=digest:return False
        choices=response['choices'];lookup={s['id']:len(s['variants']) for s in segments}
        if not isinstance(choices,list) or len(choices)!=len(lookup):return False
        seen=set()
        for c in choices:
            if not isinstance(c,dict) or set(c)!={'id','variant'} or not isinstance(c['id'],str) or c['id'] not in lookup or c['id'] in seen or type(c['variant']) is not int or not 0<=c['variant']<lookup[c['id']]:return False
            seen.add(c['id'])
        return seen==set(lookup)
