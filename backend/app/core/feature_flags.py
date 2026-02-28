import logging

from pydantic import BaseModel

_log = logging.getLogger(__name__)


class FeatureFlags(BaseModel):
    topic_v2_storage: bool = False
    topic_v2_migrate: bool = False

    def model_post_init(self, _) -> None:
        for k, v in self.model_dump().items():
            _log.info("Feature flag: %s = %s", k, v)
