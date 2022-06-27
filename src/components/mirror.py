from numpy import multiply

from .photon import Photon
from ..kernel.entity import Entity
from ..kernel.event import Event
from ..kernel.process import Process
from ..utils.encoding import polarization

from typing import TYPE_CHECKING, Any, Dict
if TYPE_CHECKING:
    from ..kernel.timeline import Timeline


class Mirror(Entity):
    
    """Single photon reflecting device.
    This class models the reflection of a single photon, in the fashion of an experimental mirror.
    Can be attached to many devices to enable different measurement options.

    Attributes:
        name (str): label for mirror instance.
        timeline (Timeline): timeline for simulation.
        fidelity (float): fraction of qubits not lost on the reflective surface
        destination (str): destination node for reflected photons
        encoding_type (Dict[str, Any]): encoding scheme of emitted photons (as defined in the encoding module).
        phase_error (float): phase error applied to qubits.
    """

    def __init__(self, name: str, timeline: "Timeline", fidelity=0.98,
                 destination="", encoding_type=polarization, phase_error=0):
        Entity.__init__(self, name, timeline)
        self.fidelity = fidelity
        self.destination = destination
        self.photon_counter = 0
        self.encoding_type = encoding_type
        self.phase_error = phase_error

    def init(self):
        pass

    def get(self, photon: Photon) -> None:
        own_encoding = self.encoding_type["name"]
        assert photon.encoding_type["name"] == own_encoding
        assert self.destination != ""
        self.photon_counter += 1

        state = photon.quantum_state.state
        rng = self.get_generator()

        # check if photon is kept
        if photon.is_null:
            photon.add_loss(1 - self.fidelity)

        elif rng.random() < self.fidelity:
            if rng.random() < self.phase_error:
                state = multiply([1, -1], state)
                photon.set_state(state)

        # otherwise, return without forwarding
        else:
            return

        self.owner.send_qubit(self.destination, photon)

    # def emit(self, state_list, dst: str) -> None:
    #
    #     time = self.timeline.now()
    #     period = int(round(1e12 / self.frequency))
    #
    #     for i, state in enumerate(state_list):
    #
    #         num_photons = 1
    #
    #         rng = self.get_generator()
    #         if rng.random() < self.phase_error:
    #             state = multiply([1, -1], state)
    #
    #         for _ in range(num_photons):
    #             wavelength = self.linewidth * rng.random() + self.wavelength
    #             new_photon = Photon(str(i),
    #                                 wavelength=wavelength,
    #                                 location=self.owner,
    #                                 encoding_type=self.encoding_type,
    #                                 quantum_state=state)
    #
    #             process = Process(self.owner, "send_qubit", [dst, new_photon])
    #
    #             event = Event(time, process)
    #             self.owner.timeline.schedule(event)
    #             self.photon_counter += 1
    #             time += period
