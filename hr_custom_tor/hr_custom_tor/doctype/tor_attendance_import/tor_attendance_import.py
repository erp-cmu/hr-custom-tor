# Copyright (c) 2025, IECMU and contributors
# For license information, please see license.txt

import os
import re
import shutil

import frappe
from frappe.model.document import Document
from frappe.utils import get_site_path, now


def insert_file_suffix_prefix(fname, suffix=None, prefix=None):
    if prefix is None:
        prefix = (
            now()[:19].replace("-", "_").replace(" ", "-").replace(":", "_")
        )  # i.e. 2025_03_15-11_30_32

    if suffix is None:
        suffix = ""

    if prefix:
        prefix = prefix + "_"

    if suffix:
        suffix = "_" + suffix

    f = fname.rsplit(".", 1)
    if len(f) == 1:
        partial, extn = f[0], ""
    else:
        partial, extn = f[0], "." + f[1]
    return f"{prefix}{partial}{suffix}{extn}"


def is_already_renamed(filepath):
    fname = os.path.basename(filepath)
    result = re.search(r"^\d{4}_\d{2}_\d{2}", fname)
    return bool(result)


class TorAttendanceImport(Document):
    def before_save(self):
        cur_filepath = self.checkin_file or None

        if cur_filepath and not is_already_renamed(cur_filepath):
            if not cur_filepath.startswith(("/private/files/", "/files/")):
                frappe.throw("File path is not valid")

            split = os.path.split(cur_filepath)
            # path_prefix with have leading "/" but not trailing "/"
            path_prefix, cur_filename = split
            # Add trailing "/" to align with the convention
            path_prefix = path_prefix + "/"

            try:
                cur_file_doc = frappe.get_last_doc(
                    "File",
                    filters={"file_url": cur_filepath},
                )
                if cur_file_doc:
                    new_filename = insert_file_suffix_prefix(cur_filename)
                    new_filepath = f"{path_prefix}{new_filename}"

                    site_path = get_site_path()  #'./SITENAME'
                    cur_filepath_site = f"{site_path}{cur_filepath}"  # The cur_filepath already contains leading "/""
                    new_filepath_site = f"{site_path}{new_filepath}"
                    shutil.copyfile(cur_filepath_site, new_filepath_site)
                    os.remove(cur_filepath_site)

                    cur_file_doc.file_url = new_filepath
                    cur_file_doc.file_name = new_filename
                    cur_file_doc.save()
                    self.checkin_file = cur_file_doc.file_url

                    # This method does not work
                    # new_file_doc = frappe.copy_doc(cur_file_doc)
                    # new_file_doc.is_private = cur_file_doc.is_private
                    # new_file_doc.file_url = new_filepath
                    # new_file_doc.file_name = new_filename
                    # new_file_doc.save(ignore_permissions=True)
                    # self.checkin_file = new_file_doc.file_url
                    # cur_file_doc.delete(ignore_permissions=True)
                else:
                    frappe.log_error("File not found.")
            except Exception as e:
                frappe.throw(
                    f"Error handling attachment: {str(e)}",
                    "Attachment Handling Exception",
                )
