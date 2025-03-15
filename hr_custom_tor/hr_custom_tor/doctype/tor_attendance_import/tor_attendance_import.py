# Copyright (c) 2025, IECMU and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now, get_site_path
import shutil
import os


def insert_file_suffix_prefix(fname, suffix=None, prefix=None):
    if prefix is None:
        prefix = (
            now()[:19].replace("-", "_").replace(" ", "-").replace(":", "_")
        )  # i.e. 2025_03_15-11_30_32

    if suffix is None:
        suffix = ""

    if not prefix:
        prefix = prefix + "_"

    if not suffix:
        suffix = "_" + suffix

    f = fname.rsplit(".", 1)
    if len(f) == 1:
        partial, extn = f[0], ""
    else:
        partial, extn = f[0], "." + f[1]
    return f"{prefix}{partial}{suffix}{extn}"


class TorAttendanceImport(Document):
    def before_save(self):
        cur_filepath = self.checkin_file or None

        if cur_filepath:
            if cur_filepath.startswith("/private/files/"):
                path_prefix = "/private/files/"
                cur_filename = cur_filepath.replace("/private/files/", "")
            elif cur_filepath.startswith("/files/"):
                path_prefix = "/files/"
                cur_filename = cur_filepath.replace("/files/", "")
            else:
                frappe.throw("File path is not valid")

            try:
                file_docs = frappe.get_all(
                    "File",
                    filters={"file_url": cur_filepath},
                    fields=["name", "is_private", "file_url"],
                )
                if file_docs:
                    old_file_doc = frappe.get_doc("File", file_docs[0]["name"])

                    new_filename = insert_file_suffix_prefix(cur_filename)
                    new_filepath = f"{path_prefix}{new_filename}"

                    site_path = get_site_path()  #'./SITENAME'
                    cur_filepath_site = f"{site_path}{cur_filepath}"  # The cur_filepath already contains leading "/""
                    new_filepath_site = f"{site_path}{new_filepath}"
                    shutil.copyfile(cur_filepath_site, new_filepath_site)
                    os.remove(cur_filepath_site)

                    new_file_doc = frappe.copy_doc(old_file_doc)
                    new_file_doc.is_private = old_file_doc.is_private
                    new_file_doc.file_url = new_filepath
                    new_file_doc.file_name = new_filename
                    new_file_doc.save(ignore_permissions=True)
                    self.checkin_file = new_file_doc.file_url
                    old_file_doc.delete(ignore_permissions=True)
                else:
                    frappe.log_error("File not found.")
            except Exception as e:
                frappe.throw(
                    f"Error handling attachment: {str(e)}",
                    "Attachment Handling Exception",
                )
