from flask import jsonify,request, current_app, abort
import inspect
from .models import MyModel
from . import app_logger, bp

model = MyModel(device="cuda")
model.model.eval()

def logger():
    app_logger.info('Client IP: %s\nAccess URL:%s\nHeaders: %s\nBody: %s\n%s', request.remote_addr,request.url, request.headers,request.get_data(),'-'*70)


@bp.route('/prediction',methods=['POST','GET'])
def pred():
    """
    Args:
        json : {'text': Org Text(str)}
    
    Returns:
        str : Summarization Text
        
    """
    if request.method=='GET':  return "The method is not allowed for the requested URL." ,405
    
    try:
        logger()
        return model.predict(str(request.get_json()['text']))
    except Exception as e:
        return f"Error: {str(e)}\n\n{pred.__doc__}"


@bp.route('/apilist')
def lists():
    """return api lists

    Returns:
        str: _description_
        
    """
    logger()
    return [rule.rule for rule in current_app.url_map.iter_rules() if not str(rule).startswith('/static')]


@bp.route('/help/<string:endpoint_name>')
def help(endpoint_name):
    """return endpoint's docstring
    
    Args:
        endpoint_name (str): endpoint
    Returns:
        str: Docstring
        
"""

    logger()
    try:
        edp = [ed.endpoint for ed in current_app.url_map.iter_rules() if (str(endpoint_name) == (ed.rule).split('/')[1])][0]
        endpoints_obj=[vf[1]  for  vf in current_app.view_functions.items() if vf[0] == edp][0]
        return inspect.getdoc(endpoints_obj)
    except Exception as e:
        return jsonify({'error': f'Endpoint {endpoint_name} not found'}), 404
    
