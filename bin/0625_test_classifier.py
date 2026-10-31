#!/usr/bin/env python3
"""Offline unit tests. No network. No FS writes outside /tmp."""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "bin"))

from openroot_classifier_loader import load  # noqa: E402

mod = load()


SSH_ENV = {
    "HOME": "/home/jesse",
    "USER": "jesse",
    "HOSTNAME": "optiplex3060",
    "PWD": "/home/jesse/openroot",
    "PREFIX": "",
}
OPTI_ENV = {
    "HOME": "/home/optiplex",
    "USER": "optiplex",
    "HOSTNAME": "optiplex-3060",
    "PWD": "/home/optiplex/openroot",
    "PREFIX": "",
}
A15_ENV = {
    "HOME": "/data/data/com.termux/files/home",
    "USER": "u0_a123",
    "HOSTNAME": "localhost",
    "PWD": "/storage/emulated/0/openroot",
    "PREFIX": "/data/data/com.termux/files/usr",
}
CONFLICT_ENV = {
    "HOME": "/data/data/com.termux/files/home",
    "USER": "jesse",
    "HOSTNAME": "optiplex3060",
    "PWD": "/storage/emulated/0/openroot",
    "PREFIX": "/data/data/com.termux/files/usr",
}


class PaneTests(unittest.TestCase):
    def test_ssh_jesse(self):
        self.assertEqual(mod.classify_pane(SSH_ENV), mod.Pane.SSH)

    def test_ssh_optiplex_inventory(self):
        self.assertEqual(mod.classify_pane(OPTI_ENV), mod.Pane.SSH)

    def test_a15(self):
        self.assertEqual(mod.classify_pane(A15_ENV), mod.Pane.A15)

    def test_conflict_unknown(self):
        self.assertEqual(mod.classify_pane(CONFLICT_ENV), mod.Pane.UNKNOWN)

    def test_prompt_wins_host(self):
        env = dict(SSH_ENV)
        env["HOSTNAME"] = "weirdbox"
        self.assertEqual(mod.classify_pane(env, "optiplex3060"), mod.Pane.SSH)


class PathTests(unittest.TestCase):
    def test_prefix_does_not_eat_jessefoo(self):
        klass, _ = mod.classify_path("/home/jessefoo/openroot", "/")
        self.assertEqual(klass, mod.PathClass.OTHER)

    def test_bus_under_mesh(self):
        klass, _ = mod.classify_path("/home/jesse/openroot/inbox/task.md", "/")
        self.assertEqual(klass, mod.PathClass.BUS)

    def test_mesh_root_is_mesh_not_bus(self):
        klass, _ = mod.classify_path("/home/jesse/openroot", "/")
        self.assertEqual(klass, mod.PathClass.MESH)

    def test_sdcard_alias(self):
        klass, _ = mod.classify_path("/sdcard/openroot/outbox/x", "/")
        self.assertEqual(klass, mod.PathClass.BUS)

    def test_syncthing_folder_is_mesh(self):
        klass, _ = mod.classify_path("/storage/emulated/0/Syncthing/openroot", "/")
        self.assertEqual(klass, mod.PathClass.MESH)

    def test_camera_roll_is_phone_not_bus(self):
        klass, _ = mod.classify_path("/storage/emulated/0/DCIM/Camera/x.jpg", "/")
        self.assertEqual(klass, mod.PathClass.PHONE)

    def test_cold_models(self):
        klass, _ = mod.classify_path("/home/optiplex/models/gguf/x.gguf", "/")
        self.assertEqual(klass, mod.PathClass.COLD)

    def test_termux_clone(self):
        klass, _ = mod.classify_path("/data/data/com.termux/files/home/openroot", "/")
        self.assertEqual(klass, mod.PathClass.CLONE)


class GateTests(unittest.TestCase):
    def admit(self, env, **kw):
        r, reason = mod.run_classifier(prompt="", env=env, quiet=True, **kw)
        self.assertEqual(r, "ADMIT", reason)

    def refuse(self, env, **kw):
        r, reason = mod.run_classifier(prompt="", env=env, quiet=True, **kw)
        self.assertEqual(r, "REFUSE", f"expected REFUSE, got ADMIT for {kw}")
        return reason

    def test_v1_table_sed_phone_on_ssh(self):
        reason = self.refuse(
            SSH_ENV,
            command="sed",
            args=["/data/data/com.termux/files/home/.ssh/config"],
        )
        self.assertIn("wrong pane", reason)

    def test_cat_inbox_on_a15(self):
        self.admit(A15_ENV, command="cat", args=["inbox/HELLO.md"])

    def test_syncthing_serve_a15(self):
        reason = self.refuse(A15_ENV, command="syncthing", args=["serve"])
        self.assertIn("Fork", reason)

    def test_rm_archive_on_a15(self):
        reason = self.refuse(A15_ENV, command="rm", args=["-rf", "/home/jesse/archive"])
        self.assertTrue("wrong pane" in reason or "cold" in reason.lower() or "BOX" in reason)

    def test_echo_outbox_on_ssh_write(self):
        self.admit(SSH_ENV, command="tee", args=["outbox/test"], bus_only=True)

    def test_write_mesh_root_refused(self):
        reason = self.refuse(
            SSH_ENV,
            command="tee",
            args=["/home/jesse/openroot/kernel/wipe.py"],
            bus_only=True,
        )
        self.assertIn("mesh root", reason)

    def test_write_camera_roll_refused(self):
        reason = self.refuse(
            A15_ENV,
            command="cp",
            args=["/storage/emulated/0/DCIM/Camera/x.jpg"],
            bus_only=True,
        )
        self.assertIn("continent", reason)

    def test_wipe_id_without_utd(self):
        reason = self.refuse(
            SSH_ENV,
            command="syncthing",
            args=["--reset-database"],
            folder_state="OUT_OF_DATE",
        )
        self.assertIn("UP_TO_DATE", reason)

    def test_conflict_pane(self):
        r, reason = mod.run_classifier(prompt="", env=CONFLICT_ENV, quiet=True)
        self.assertEqual(r, "REFUSE")
        self.assertIn("Unknown pane", reason)

    def test_cwd_phone_on_ssh(self):
        env = dict(SSH_ENV)
        env["PWD"] = "/storage/emulated/0/openroot"
        reason = self.refuse(env, command="ls")
        self.assertIn("PHONE", reason or "")


if __name__ == "__main__":
    unittest.main()
