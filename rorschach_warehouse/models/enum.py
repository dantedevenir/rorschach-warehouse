from .policies.enum import Status
from .providers.enum import Name
from .providers.enum import Type
from .providers.source.enum import SourceType
from .policies.group.enum import MemberType

enumModel = {
    Status: "policies",
    Name: "providers",
    Type: "providers",
    SourceType: "providers",
    MemberType: "policies",
}