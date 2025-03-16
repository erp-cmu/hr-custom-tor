// Copyright (c) 2025, IECMU and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tor Attendance Import", {
  setup(frm) {
    console.log("setup");
    frm.has_import_file = () => {
      return Boolean(frm.doc.checkin_file);
    };
  },
  refresh(frm) {
    console.log(frm);
    console.log("refresh");
    frm.refresh_fields();
  },

  onload_post_render(frm) {
    console.log("onload_post_render");
    frm.trigger("update_primary_action");
  },

  checkin_file(frm) {
    console.log("checkin_file");
    frm.trigger("update_primary_action");
  },

  start_import(frm) {
    console.log("start_import");
    frm
      .call({
        method: "form_start_import",
        args: { data_import: frm.doc.name },
        btn: frm.page.btn_primary,
      })
      .then((r) => {
        console.log(r);
        frm.refresh();
      });
  },

  update_primary_action(frm) {
    console.log({ frm, is_new: frm.is_new() });
    console.log("update_primary_action");
    if (frm.is_dirty()) {
      frm.enable_save();
      return;
    }
    frm.disable_save();
    if (!frm.is_new() && frm.has_import_file()) {
      let label = __("Start Import");
      frm.page.set_primary_action(label, () => frm.events.start_import(frm));
    } else {
      frm.page.set_primary_action(__("Save"), () => frm.save());
    }
  },
});
