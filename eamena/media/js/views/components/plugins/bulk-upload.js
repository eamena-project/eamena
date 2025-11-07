import $ from 'jquery';
import ko from 'knockout';
import arches from 'arches';

import BulkUploaderTemplate from 'templates/views/components/plugins/bulk-upload.htm';

export default ko.components.register('bulk-upload', {

		viewModel: function(params) {

		    var self = this; console.log(self);

		    $("#upload-validate").prop('disabled', true);
		    $("#upload-convert").prop('disabled', true);

                    $('input#append').on('change', function() {
		    	$("#upload-convert").prop('disabled', true);
                    });


		    $('#excelfileupload').on('change', function() {
			var csrftoken = $("[name=csrfmiddlewaretoken]").val();
			var url = $(this).data("url");
			var postdata = new FormData($("#file-uploader")[0]);
		    	$("#upload-validate").prop('disabled', true);
		    	$("#upload-convert").prop('disabled', true);
			$('#bu-loading').css('visibility', 'visible');
			$.ajax({
				url: url,
				method: 'POST',
				data: postdata,
				processData: false,
				contentType: false,
			        beforeSend: function(request) {
			            request.setRequestHeader("X-CSRFToken",csrftoken);
			        },
			        complete: function(e) {
					var data = e.responseJSON;
					var valid = data.filevalid;
					if(valid)
					{
						var filename = data.filename;
						var uuid = data.upload;
						var csrf = data.csrf;
						$("#upload-uuid").val(uuid);
						$("#upload-filename").val(filename);
						$("#upload-validate").prop('disabled', false);
		    				$("#upload-convert").prop('disabled', true);
						$("[name=csrfmiddlewaretoken]").val(csrf);
					}
					else
					{
						$("#upload-validate").prop('disabled', true);
						$("#upload-convert").prop('disabled', true);
					}
					$('#bu-loading').css('visibility', 'hidden');
			        },
				error: function(e) {
					$("#upload-validate").prop('disabled', true);
					$("#upload-convert").prop('disabled', true);
					$('.uploader-output').html("Uploading the file failed. Please check your connectivity.");
					$('#bu-loading').css('visibility', 'hidden');
				}
			});
		    });

		    $('#upload-convert').on('click', function() {

			var uuid = $("#upload-uuid").val();
			var graphid = $("#upload-graphid").val();
			var appendmode = 'no';
			var csrftoken = $("[name=csrfmiddlewaretoken]").val();
			var url = $("#convert-form").attr("action");

			$('.uploader-output').html("<p>Uploading...</p>");
			if($("input#append").prop("checked")) { appendmode = 'yes'; }

			var postdata = new FormData();
			postdata.append('uploadid', uuid);
			postdata.append('graphid', graphid);
			postdata.append('append', appendmode);

			$('#bu-loading').css('visibility', 'visible');
			$.ajax({
				url: url,
				method: 'POST',
				data: postdata,
				processData: false,
				contentType: false,
			        beforeSend: function(request) {
			        	request.setRequestHeader("X-CSRFToken",csrftoken);
			        },
			        success: function(data) {
					$('#bu-loading').css('visibility', 'hidden');
					if(data['success'])
					{
						if(data['notification'])
						{
							$('.uploader-output').html("<p>Upload successful!</p><p>The data will be imported soon, and a notification will be sent to " + data['notification'] + "</p>");
						} else {
							$('.uploader-output').html("<p>Upload successful!</p><p>The data will be imported soon.</p>");
						}
					} else {
						$('.uploader-output').html("<p>Upload failed!</p>");
					}
					$("#upload-validate").prop('disabled', true);
					$("#upload-convert").prop('disabled', true);
			        },
				error: function(e) {
					$("#upload-validate").prop('disabled', true);
					$("#upload-convert").prop('disabled', true);
					$('.uploader-output').html("<p>Upload failed!</p>");
					$('#bu-loading').css('visibility', 'hidden');
				}
			});

		    });

		    $('#upload-validate').on('click', function() {

			var uuid = $("#upload-uuid").val();
			var graphid = $("#upload-graphid").val();
			var appendmode = 'no';
			var csrftoken = $("[name=csrfmiddlewaretoken]").val();
			var url = $("#validate-form").attr("action");

			$('.uploader-output').html("<p>Validating...</p>");
			if($("input#append").prop("checked")) { appendmode = 'yes'; }

			var postdata = new FormData();
			postdata.append('uploadid', uuid);
			postdata.append('graphid', graphid);
			postdata.append('append', appendmode);

			$('#bu-loading').css('visibility', 'visible');
			$.ajax({
				url: url,
				method: 'POST',
				data: postdata,
				processData: false,
				contentType: false,
			        beforeSend: function(request) {
			            request.setRequestHeader("X-CSRFToken",csrftoken);
			        },
			        success: function(data) {
					//var data = e.responseJSON;
					var html = ''
					var c = data.length;
					for(var i = 0; i < c; i++)
					{
						var item = data[i];
						html = html + '<tr>';
						html = html + '<td style="padding-right: 1em; vertical-align: top;"><strong>' + item[0] + '</strong></td>';
						html = html + '<td>';
						html = html + item[1];
						if(item[2] != '') { html = html + '<br/><small>' + item[2] + '</small>'; }
						html = html + '</td>';
						html = html + '</tr>';
					}
					if(html != '') { html = '<p>The file did not validate, and needs to be corrected. A summary of the errors encountered is below.</p><table>' + html + '</html>'; }
					if(html == '')
					{
						$('.uploader-output').html("<p>The file validated successfully and may now be scheduled for importing.</p><p>Please click the 'Upload' button to proceed.</p>");
						$("#upload-convert").prop('disabled', false);
					}
					else
					{
						$('.uploader-output').html(html);
					}
					$('#bu-loading').css('visibility', 'hidden');
			        },
				error: function(e) {
					$("#upload-validate").prop('disabled', true);
					$("#upload-convert").prop('disabled', true);
					$('.uploader-output').html("<p>Validation failed due to an upload error.</p>");
					$('#bu-loading').css('visibility', 'hidden');
				}
			});


                });

		},
		template: BulkUploaderTemplate

});
