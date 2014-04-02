from boto.elastictranscoder.layer1 import ElasticTranscoderConnection

# environment variables:
# AWS_ACCESS_KEY_ID
# AWS_SECRET_ACCESS_KEY
transcoder = ElasticTranscoderConnection()
# op_pipeline_id ="1394732373162-pgxcqg"
op_pipeline_id ="1394890860589-au68g9"
preset_id = "1394891139418-5okr3u"

op_input_name = {
					"Key":"demo1",
					"FrameRate":"auto",
					"Resolution":"auto",
					"AspectRatio":"auto",
					"Container": "webm"
				}
op_outputs = [
			  	{
				  "Key": "demo1",
				  "FrameRate": "auto",
				  "PresetId": preset_id,
				  "Watermarks": [
									    {
									      "PresetWatermarkId": "BottomRight",
									      "InputKey": "logo.png"
									    }
								  ],
				}
			]
op_output_key_prefix = "m/transcoded-"
transcoder.create_job(pipeline_id=op_pipeline_id, outputs=op_outputs, input_name=op_input_name, output_key_prefix = op_output_key_prefix)