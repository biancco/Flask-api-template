import json
import io
import inspect
import base64
from flask import (
    jsonify, 
    request, 
    current_app, 
    Blueprint,
    send_file
)
from PIL import Image
from .models import SumModel, ObjectDetector, DepthEstimation, TTSModel, STTModel
from .k_fashion_detection.detect_model_hold import KF_Detector

blueprint=Blueprint('prediction',
             __name__,
             url_prefix=''
)

sum_model = SumModel(device="cuda")
# od_model = ObjectDetector(device="cuda")
od_model = KF_Detector(device="cuda")
de_model = DepthEstimation(device="cuda")
tts_model = TTSModel(device="cuda")
stt_model = STTModel(device="cuda")

def logger():
    current_app.logger.info('Client IP: %s\nAccess URL:%s\nHeaders: %s\nBody: %s\n%s', request.remote_addr,request.url, request.headers,request.get_data(),'-'*70)


# -------------------------------------------------
# Input: Json
# Output: text
# -------------------------------------------------
@blueprint.route('/prediction',methods=['POST','GET'])
def prediction():
    """
    Args:
        json : {'text': Org Text(str)}
    
    Returns:
        str : Summarization Text
        
    """
    if request.method=='GET':  return "The method is not allowed for the requested URL." ,405
    
    try:
        logger()
        return sum_model.predict(str(request.get_json()['text']))
    except Exception as e:
        return f"Error: {str(e)}\n\n{prediction.__doc__}"


# -------------------------------------------------
# Input: Image + Json
# Output: Json
# -------------------------------------------------
@blueprint.route('/object_detection',methods=['POST','GET'])
def object_detection():
    try:
        # read data
        data = json.load(request.files['data'])
        
        # [('dog', [0.21, 64.61, 383.16, 494.14], 0.999), ('dog', [328.2, 125.86, 714.74, 461.77], 0.995)]
        # read image
        uploaded_file = request.files['image']
        file_content = uploaded_file.read()
        image = Image.open(io.BytesIO(file_content))
        preds = od_model.predict(image)
        
        # 추론 결과를 시각화하려면 아래 사용 (저장위치 : k_fashion_detection/runs/server)
        # preds = od_model.predict(image, nosave=False)

        return jsonify(preds), 200
    except Exception as e:
        return f"Error: {str(e)}\n\n{object_detection.__doc__}"


# -------------------------------------------------
# Input: Image + Json
# Output: Image
# -------------------------------------------------
@blueprint.route('/depth_estimation',methods=['POST','GET'])
def depth_estimation():
    try:        
        # read image
        uploaded_file = request.files['image']
        file_content = uploaded_file.read()
        image = Image.open(io.BytesIO(file_content))
        image_pred = de_model.predict(image)
        image_pred_bytes_io = io.BytesIO()
        image_pred.save(image_pred_bytes_io, format='PNG')
        image_pred_bytes_io.seek(0, io.SEEK_SET)
        return send_file(image_pred_bytes_io, download_name="result.png", as_attachment=True), 200
    except Exception as e:
        return f"Error: {str(e)}\n\n{depth_estimation.__doc__}"


# -------------------------------------------------
# Input: Image + Json
# Output: Json(Base64(Image bytes))
# -------------------------------------------------
@blueprint.route('/depth_estimation_json',methods=['POST','GET'])
def depth_estimation_json():
    try:        
        # read image
        uploaded_file = request.files['image']
        file_content = uploaded_file.read()
        image = Image.open(io.BytesIO(file_content))
        image_pred = de_model.predict(image)
        image_pred_bytes_io = io.BytesIO()
        image_pred.save(image_pred_bytes_io, format='PNG')
        return jsonify({
            "data": base64.b64encode(image_pred_bytes_io.getvalue()).decode("utf-8"),
            "file_name": "depth_estimation_json.png",
            "desc": "this is a test description.",
            }), 200
    except Exception as e:
        return f"Error: {str(e)}\n\n{depth_estimation_json.__doc__}"


# -------------------------------------------------
# Input: Json
# Output: Audio
# -------------------------------------------------
@blueprint.route('/text2speech',methods=['POST','GET'])
def text2speech():
    try:        
        tts_res_bytes = tts_model.predict(str(request.get_json()['text']))
        return send_file(io.BytesIO(tts_res_bytes), download_name="result.wav", as_attachment=True), 200
    except Exception as e:
        return f"Error: {str(e)}\n\n{text2speech.__doc__}"


# -------------------------------------------------
# Input: Audio + Json
# Output: Json
# -------------------------------------------------
@blueprint.route('/speech2text',methods=['POST','GET'])
def speech2text():
    try:
        uploaded_file = request.files['audio']
        stt_res = stt_model.predict(uploaded_file.read())
        return jsonify({"transcript": stt_res}), 200
    except Exception as e:
        return f"Error: {str(e)}\n\n{text2speech.__doc__}"
    

@blueprint.route('/apilist')
def lists():
    """return api lists

    Returns:
        str: _description_
        
    """
    logger()
    return [rule.rule for rule in current_app.url_map.iter_rules() if not str(rule).startswith('/static')]


@blueprint.route('/help/<string:endpoint_name>')
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
    
