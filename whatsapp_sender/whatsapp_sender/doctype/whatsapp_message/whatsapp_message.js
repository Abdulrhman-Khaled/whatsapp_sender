frappe.ui.form.on("whatsapp message", {
	refresh: function (frm) {

		frm.add_custom_button(__("Send Test Message"), function () {

			frm.call("msg", {
				token: frm.doc.token,
				deviceId: frm.doc.device_id,
				recipient: frm.doc.to,
				url: frm.doc.url,
			}).then(r => {
				frappe.msgprint(r.message);;
			})
		});
	}
});
