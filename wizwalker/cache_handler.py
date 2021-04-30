import json
from collections import defaultdict
from functools import cached_property
from pathlib import Path
from typing import List, Union

import aiofiles
from loguru import logger

from wizwalker import Wad, utils


class CacheHandler:
    def __init__(self):
        self.wad_cache = None
        self.template_ids = None
        self.node_cache = None

    @cached_property
    def install_location(self) -> Path:
        """
        Wizard101 install location
        """
        return utils.get_wiz_install()

    @cached_property
    def cache_dir(self):
        """
        The dir parsed data is stored in
        """
        return utils.get_cache_folder()

    async def check_updated(self, wad_file: Wad, files: Union[List[str], str]):
        """
        Checks if some wad files have changed since we last accessed them
        """
        if isinstance(files, str):
            files = [files]

        if not self.wad_cache:
            self.wad_cache = await self.get_wad_cache()

        res = []
        has_updated = False

        for file_name in files:
            file_info = await wad_file.get_file_info(file_name)

            if self.wad_cache[wad_file.name][file_name] != file_info.size:
                has_updated = True
                logger.info(
                    f"{file_name} has updated. old: {self.wad_cache[wad_file.name][file_name]} new: {file_info.size}"
                )
                res.append(file_name)
                self.wad_cache[wad_file.name][file_name] = file_info.size

            else:
                logger.info(f"{file_name} has not updated from {file_info.size}")

        if has_updated:
            await self.write_wad_cache()

        return res

    async def cache(self):
        """
        Caches various file data
        """
        root_wad = Wad.from_game_data("Root")

        logger.info("Caching template if needed")
        await self._cache_template(root_wad)

    async def _cache_template(self, root_wad):
        template_file = "TemplateManifest.xml"

        template_file = await self.check_updated(root_wad, template_file)

        if template_file:
            file_data = await root_wad.get_file("TemplateManifest.xml")
            pharsed_template_ids = utils.pharse_template_id_file(file_data)
            del file_data

            async with aiofiles.open(self.cache_dir / "template_ids.json", "w+") as fp:
                json_data = json.dumps(pharsed_template_ids)
                await fp.write(json_data)

    async def _cache_nodes(self):
        self.node_cache = await self.get_node_cache()

        game_data = self.install_location / "Data" / "GameData"
        all_wads = game_data.glob("*.wad")

        new_node_data = {}
        for wad_name in all_wads:
            wad_name = wad_name.name
            if not self.node_cache[wad_name]:
                logger.info(f"Checking {wad_name} for node data")
                wad = Wad.from_game_data(wad_name)
                self.node_cache[wad_name] = 1

                try:
                    file_info = await wad.get_file_info("pathNodeData.bin")
                    if file_info.size == 20:
                        continue

                    node_data = await wad.get_file("pathNodeData.bin")
                except RuntimeError:
                    continue
                else:
                    pharsed_node_data = utils.pharse_node_data(node_data)
                    new_node_data[wad_name] = pharsed_node_data

        if new_node_data:
            node_data_json = self.cache_dir / "node_data.json"
            if node_data_json.exists():
                async with aiofiles.open(node_data_json) as fp:
                    json_data = await fp.read()
                    old_node_data = json.loads(json_data)

            else:
                old_node_data = {}

            old_node_data.update(new_node_data)

            async with aiofiles.open(node_data_json, "w+") as fp:
                json_data = json.dumps(old_node_data)
                await fp.write(json_data)

        await self.write_node_cache()

    async def get_template_ids(self) -> dict:
        """
        Loads template ids from cache

        Raises:
            RuntimeError: template ids haven't been cached yet

        Returns:
            the loaded template ids
        """
        await self.cache()
        async with aiofiles.open(self.cache_dir / "template_ids.json") as fp:
            message_data = await fp.read()

        return json.loads(message_data)

    async def get_wad_cache(self) -> dict:
        """
        Gets the wad cache data

        Returns:
            a dict with the current cache data
        """
        try:
            async with aiofiles.open(self.cache_dir / "wad_cache.data") as fp:
                data = await fp.read()
        except OSError:
            data = None

        wad_cache = defaultdict(lambda: defaultdict(lambda: -1))

        if data:
            wad_cache_data = json.loads(data)

            # this is so the default dict inside the default dict isn't replaced
            # by .update
            for k, v in wad_cache_data.items():
                for k1, v1 in v.items():
                    wad_cache[k][k1] = v1

        return wad_cache

    async def write_wad_cache(self):
        """
        Writes wad cache to disk
        """
        async with aiofiles.open(self.cache_dir / "wad_cache.data", "w+") as fp:
            json_data = json.dumps(self.wad_cache)
            await fp.write(json_data)

    async def get_node_cache(self) -> dict:
        """
        Loads the node cache from disk

        Returns:
            The current node cache data
        """
        try:
            async with aiofiles.open(self.cache_dir / "node_cache.data") as fp:
                data = await fp.read()
        except OSError:
            data = None

        node_cache = defaultdict(lambda: 0)

        if data:
            node_cache_data = json.loads(data)
            node_cache.update(node_cache_data)

        return node_cache

    async def write_node_cache(self):
        """
        Writes node cache to disk
        """
        async with aiofiles.open(self.cache_dir / "node_cache.data", "w+") as fp:
            json_data = json.dumps(self.node_cache)
            await fp.write(json_data)
