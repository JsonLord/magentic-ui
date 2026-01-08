from __future__ import annotations

import asyncio
import logging
import os
import secrets
import socket
import subprocess
from autogen_core import Component
from pydantic import BaseModel

from .base_playwright_browser import PlaywrightBrowser


# Configure logging
logger = logging.getLogger(__name__)


class VncSubprocessPlaywrightBrowserConfig(BaseModel):
    """
    Configuration for the VNC Subprocess Playwright Browser.
    """

    playwright_port: int = 37367
    novnc_port: int = 6080
    playwright_websocket_path: str | None = None


class VncSubprocessPlaywrightBrowser(
    PlaywrightBrowser, Component[VncSubprocessPlaywrightBrowserConfig]
):
    """
    A Playwright browser implementation with VNC support for visual interaction, running as a subprocess.
    Provides both programmatic browser control via Playwright and visual access through noVNC.
    """

    component_config_schema = VncSubprocessPlaywrightBrowserConfig
    component_type = "other"

    def __init__(
        self,
        *,
        playwright_port: int = 37367,
        playwright_websocket_path: str | None = None,
        novnc_port: int = 6080,
    ):
        super().__init__()
        self._playwright_port = playwright_port
        self._novnc_port = novnc_port
        self._playwright_websocket_path = (
            playwright_websocket_path or secrets.token_hex(16)
        )
        self._hostname = "127.0.0.1"
        self._processes: list[asyncio.subprocess.Process] = []

    async def __aenter__(self) -> None:
        logger.info("Starting browser subprocesses...")
        try:
            # 1. Start Xvfb
            xvfb_proc = await asyncio.create_subprocess_exec(
                "Xvfb", ":99", "-screen", "0", "1440x900x24", "-ac", "-nolisten", "tcp",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self._processes.append(xvfb_proc)
            await asyncio.sleep(1)

            env = os.environ.copy()
            env["DISPLAY"] = ":99"

            # 2. Start openbox
            openbox_proc = await asyncio.create_subprocess_exec(
                "openbox-session",
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self._processes.append(openbox_proc)

            # 3. Start x11vnc
            x11vnc_proc = await asyncio.create_subprocess_exec(
                "x11vnc", "-display", ":99", "-forever", "-shared", "-nopw",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self._processes.append(x11vnc_proc)

            # 4. Start novnc
            novnc_proc = await asyncio.create_subprocess_exec(
                "novnc", "--vnc", "localhost:5900", "--listen", str(self._novnc_port),
                 stdout=subprocess.PIPE,
                 stderr=subprocess.PIPE
            )
            self._processes.append(novnc_proc)

            # 5. Start playwright-server
            playwright_env = env.copy()
            playwright_env["WS_PATH"] = self._playwright_websocket_path
            playwright_env["PLAYWRIGHT_PORT"] = str(self._playwright_port)

            script_path = "docker/magentic-ui-browser-docker/playwright-server.js"

            playwright_proc = await asyncio.create_subprocess_exec(
                "node", script_path,
                env=playwright_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self._processes.append(playwright_proc)

            await asyncio.sleep(5)

            await super().__aenter__()
        except FileNotFoundError as e:
            logger.error(f"Failed to start browser subprocesses: {e}. Make sure all dependencies (Xvfb, openbox, x11vnc, novnc, node) are installed and in your PATH.")
            await self.__aexit__(None, None, None)
            raise
        except Exception as e:
            logger.error(f"Failed to start browser subprocesses: {e}")
            await self.__aexit__(None, None, None)
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await super().__aexit__(exc_type, exc_val, exc_tb)
        logger.info("Stopping browser subprocesses...")
        for proc in reversed(self._processes):
            try:
                proc.terminate()
                await asyncio.wait_for(proc.wait(), timeout=5)
            except (ProcessLookupError, asyncio.TimeoutError):
                proc.kill()
                await proc.wait()
            except Exception as e:
                logger.error(f"Error stopping process {proc.pid}: {e}")
        self._processes = []


    def _get_available_port(self) -> tuple[int, socket.socket]:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
        return port, s

    def _generate_new_browser_address(self) -> None:
        self._playwright_port, playwright_sock = self._get_available_port()
        self._novnc_port, novnc_sock = self._get_available_port()
        self._hostname = "127.0.0.1"
        playwright_sock.close()
        novnc_sock.close()

    @property
    def browser_address(self) -> str:
        return f"ws://{self._hostname}:{self._playwright_port}/{self._playwright_websocket_path}"

    @property
    def vnc_address(self) -> str:
        return f"http://{self._hostname}:{self._novnc_port}/vnc.html"

    @property
    def novnc_port(self) -> int:
        return self._novnc_port

    @property
    def playwright_port(self) -> int:
        return self._playwright_port

    def _to_config(self) -> VncSubprocessPlaywrightBrowserConfig:
        return VncSubprocessPlaywrightBrowserConfig(
            playwright_port=self._playwright_port,
            novnc_port=self._novnc_port,
            playwright_websocket_path=self._playwright_websocket_path,
        )

    @classmethod
    def _from_config(
        cls, config: VncSubprocessPlaywrightBrowserConfig
    ) -> "VncSubprocessPlaywrightBrowser":
        return cls(
            playwright_port=config.playwright_port,
            novnc_port=config.novnc_port,
            playwright_websocket_path=config.playwright_websocket_path,
        )
