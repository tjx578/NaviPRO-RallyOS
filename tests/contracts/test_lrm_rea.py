from pathlib import Path
import sys
import pytest
import yaml
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'python/src'))
from navipro_rallyos.route.lrm_review import validate_lrm_proposal, ReviewGateError
TRUST={'route_revision_id':'RR-7','graph_dataset_id':'bali-graph-v1','profile_digest':'sha256:car',
       'official_anchor_ids':['START','KM-PAL','FINISH'],'candidate_ids':['C1','C2']}
P={'mode':'REVIEW','route_revision_id':'RR-7','graph_dataset_id':'bali-graph-v1',
   'profile_digest':'sha256:car','official_anchor_ids':['START','KM-PAL','FINISH'],
   'selected_candidate_id':'C1','proposed_shaping_points':[]}
SHAPE={'after_anchor_id':'START','lat_e7':-86700000,'lon_e7':1152100000,'reason':'inspect candidate',
       'status':'DRAFT_PROPOSAL','authority':'AGENT_PROPOSE'}

def test_valid_review_no_authority():
    output=validate_lrm_proposal({**P,'proposed_shaping_points':[SHAPE]},TRUST)
    assert output['status']=='PROPOSAL_ONLY'
    assert output['route_authority'] is False
    assert output['official_anchor_ids']==TRUST['official_anchor_ids']
    assert output['shaping_proposals'][0]['after_anchor_id']=='START'

def test_modified_order_or_missing_anchor_rejected():
    for order in [['START','FINISH','KM-PAL'],['START','FINISH'],['FINISH','KM-PAL','START']]:
        with pytest.raises(ReviewGateError):validate_lrm_proposal({**P,'official_anchor_ids':order},TRUST)

def test_live_and_invalid_revision_graph_or_candidate_rejected():
    for update in [{'mode':'LIVE'},{'route_revision_id':'old'},{'graph_dataset_id':'different'},
                   {'profile_digest':'different'},{'selected_candidate_id':'C404'}]:
        with pytest.raises(ReviewGateError):validate_lrm_proposal({**P,**update},TRUST)

def test_authority_and_ui_mutations_disallowed_in_payload():
    for field,value in [('route_authority',True),('approved',True),('publish',True),
                        ('waypoints',[]),('source_anchor_order',[]),('reverseWaypoints',True),('confirm',False)]:
        with pytest.raises(ReviewGateError):validate_lrm_proposal({**P,field:value},TRUST)

def test_shaping_rules_reject_invalid_coordinates_and_status():
    for q in [{'after_anchor_id':'FINISH'},{'lat_e7':True},{'lon_e7':float('nan')},
              {'authority':'NAVIGATOR_ONLY'},{'status':'VERIFIED'},{'reason':''}]:
        with pytest.raises(ReviewGateError):validate_lrm_proposal({**P,'proposed_shaping_points':[{**SHAPE,**q}]},TRUST)

def test_response_cannot_mutate_trusted_anchors():
    response=validate_lrm_proposal(P,TRUST)
    response['official_anchor_ids'].reverse()
    assert TRUST['official_anchor_ids']==['START','KM-PAL','FINISH']

def test_source_capability_registry_and_mcp_boundary():
    registry=yaml.safe_load((ROOT/'contracts/routing/lrm-capability-registry.yaml').read_text())
    assert len(registry['capabilities'])>=30
    assert len({x['id'] for x in registry['capabilities']})==len(registry['capabilities'])
    assert all(x['modes']==['PREP','REVIEW'] and x['authority']=='CANDIDATE_ONLY' for x in registry['capabilities'])
    spec=yaml.safe_load((ROOT/'contracts/openapi/navipro-rallyos.openapi.yaml').read_text())
    ops=[o for p,item in spec['paths'].items() if p.startswith('/routing-ui/lrm/') for method,o in item.items()]
    assert len(ops)>=5
    ids=[x['operationId'] for x in ops]
    assert len(ids)==len(set(ids))
    for op in ops:
        assert op['x-navipro-mode']==['PREP','REVIEW']
        assert op['x-navipro-authority'] in ('READ','AGENT_PROPOSE','UI_ONLY')
        assert op['x-navipro-side-effect']=='NONE'
        assert 'confirm' not in op['operationId'].lower()
