import enum

from .. import download
from .. import idol
from .. import util
from .. import idoltype
from ..idol import error

import pydantic

_TARGET_OS_REMAP = {"Android": idoltype.PlatformType.Android, "iOS": idoltype.PlatformType.iOS}


class DownloadTargetOS(str, enum.Enum):
    ANDROID = "Android"
    IPHONE = "iOS"


class DownloadPackageType(enum.IntEnum):
    BOOTSTRAP = 0
    LIVE = 1
    SCENARIO = 2
    SUBSCENARIO = 3
    MICRO = 4
    EVENT_SCENARIO = 5
    MULTI_UNIT_SCENARIO = 6


class DownloadUpdateRequest(pydantic.BaseModel):
    target_os: DownloadTargetOS
    install_version: str
    external_version: str
    package_list: list[int] = []


class DownloadBatchRequest(pydantic.BaseModel):
    client_version: str
    os: DownloadTargetOS
    package_type: DownloadPackageType
    excluded_package_ids: list[int] = []


class DownloadAdditionalRequest(pydantic.BaseModel):
    target_os: DownloadTargetOS
    client_version: str
    package_type: DownloadPackageType
    package_id: int


class DownloadResponse(pydantic.BaseModel):
    size: str
    url: str


class DownloadUpdateResponse(DownloadResponse):
    version: str


class DownloadGetUrlRequest(pydantic.BaseModel):
    os: DownloadTargetOS
    path_list: list[str]


class DownloadGetUrlResponse(pydantic.BaseModel):
    url_list: list[str]


@idol.register("/download/update", check_version=False, batchable=False)
def update(context: idol.SchoolIdolAuthParams, request: DownloadUpdateRequest) -> list[DownloadUpdateResponse]:
    try:
        install_version = util.parse_sif_version(request.install_version)
        external_version = util.parse_sif_version(request.external_version)
        target_version = min(external_version, install_version)
    except ValueError as e:
        raise error.IdolError(detail=str(e))

    links = download.get_update_files(context.request, _TARGET_OS_REMAP[str(request.target_os)], target_version)
    return [DownloadUpdateResponse(url=link.url, size=str(link.size), version=link.version) for link in links]


@idol.register("/download/batch", check_version=False, batchable=False)
def batch(context: idol.SchoolIdolAuthParams, request: DownloadBatchRequest) -> list[DownloadResponse]:
    links = download.get_batch_files(
        context.request, _TARGET_OS_REMAP[str(request.os)], int(request.package_type), request.excluded_package_ids
    )
    return [DownloadResponse(url=link.url, size=str(link.size)) for link in links]


@idol.register("/download/event", check_version=False, batchable=False)
def event(context: idol.SchoolIdolAuthParams, request: DownloadBatchRequest) -> list[DownloadResponse]:
    # TODO
    return []


@idol.register("/download/additional", check_version=False, batchable=False)
def additional(context: idol.SchoolIdolAuthParams, request: DownloadAdditionalRequest) -> list[DownloadResponse]:
    links = download.get_single_package(
        context.request, _TARGET_OS_REMAP[request.target_os], int(request.package_type), request.package_id
    )
    if links is None:
        raise error.IdolError(error.ERROR_DOWNLOAD_NO_ADDITIONAL_PACKAGE)
    return [DownloadResponse(url=link.url, size=str(link.size)) for link in links]


@idol.register("/download/getUrl", check_version=False, batchable=False)
def geturl(context: idol.SchoolIdolAuthParams, request: DownloadGetUrlRequest) -> DownloadGetUrlResponse:
    links = download.get_raw_files(context.request, _TARGET_OS_REMAP[request.os], request.path_list)
    return DownloadGetUrlResponse(url_list=[link.url for link in links])
