from datetime import datetime, timedelta
from typing import Iterable, NewType
from dataclasses import dataclass
from lxml import etree
import random as rnd
import os


KByte = NewType("KByte", int)

G_LOCATION: tuple[str, ...] = (
    "london",
    "undefined",
    "moscow",
    "thailand",
    "new-york",
    "sidney",
    "hamburg",
    "helsinki",
)

G_DATA_FOLDER: str = "data"
G_STORAGE_TYPES: tuple[str, ...] = ("raw", "compressed", "lite")
G_CHUNK_SIZE: KByte = KByte(10)

G_IID_MAP: dict[tuple[str, str, str], str] = {}


@dataclass(slots=True, frozen=True)
class Manifest:
    date: str
    available: "Iterable[Payload]"

    def create(self):
        year, month, day = self.date.split("-")
        path = os.path.join(G_DATA_FOLDER, year, month, day)

        os.makedirs(path, exist_ok=True)

        xml_tree = self.__generate_xml()
        content = etree.tostring(xml_tree, encoding=str, pretty_print=True)

        print(f"==Creating {path}/manifest.xml ... ", end="")

        with open(os.path.join(path, "manifest.xml"), "w") as f:
            f.write(content)
            print(f"OK")

        for payload in self.available:
            payload.fill_binary_file(date, rnd.randint(250, 1080), G_CHUNK_SIZE)

    def __generate_xml(self) -> etree._Element:  # type: ignore
        root = etree.Element("ManifestRoot")
        date = etree.SubElement(root, "Date")
        date.text = self.date

        exchs = etree.SubElement(root, "Exchanges")

        exch_memo: set[str] = set()
        inst_memo: set[str] = set()
        for payload in self.available:
            if payload.exchange not in exch_memo:
                loc = G_LOCATION[rnd.randint(0, 7)]
                exch = etree.SubElement(
                    exchs,
                    "Exchange",
                    {
                        "Name": payload.exchange,
                        "Location": loc,
                    },
                )
                exch_memo.add(payload.exchange)
            else:
                exch: etree._Element = exchs.xpath(f"/Exchange[@Name={payload.exchange}]")[0]  # type: ignore
                loc = exch.get("Location")
                assert loc is not None, f"Location is empty for {payload.exchange}"

            isins = etree.SubElement(exch, "Instruments")

            if payload.instrument not in inst_memo:
                iid_key = (payload.exchange, loc, payload.instrument)
                if (iid := G_IID_MAP.get(iid_key)) is None:
                    iid = str(rnd.randint(0, 255))
                    G_IID_MAP[iid_key] = iid

                etree.SubElement(
                    isins,
                    "Instrument",
                    {
                        "Name": payload.instrument,
                        "StorageType": G_STORAGE_TYPES[rnd.randint(0, 2)],
                        "Levels": str(payload.levels),
                        "Iid": iid,
                        "AvailableIntervalBegin": f"{rnd.randint(0,15)}:{rnd.randint(0,59)}",
                        "AvailableIntervalEnd": f"{rnd.randint(16,23)}:{rnd.randint(0,59)}",
                    },
                )

        return root


@dataclass(slots=True, frozen=True)
class Payload:
    instrument: str
    exchange: str
    levels: list[int]

    def __produce_binary_chunk(self, chunk_size: KByte) -> bytes:
        if chunk_size < 1:
            raise BufferError("chunk_size is too small")

        isin = bytes(self.instrument, encoding="utf-8")
        exch = bytes(self.exchange, encoding="utf-8")
        level = b"".join(
            (level.to_bytes(4) for level in self.levels)
        )  # might raise OverflowError if level is too big
        header_sz = len(isin) + len(exch) + 4

        if (noise_len := ((chunk_size * 1024) - header_sz)) < 0:
            raise BufferError(
                f"Chunk size is too small. "
                f"Header has taken '{header_sz}' bytes, but chunk requires '{chunk_size * 1024}' bytes. "
                f"[delta = {noise_len}]"
            )

        noise = rnd.randbytes(noise_len)
        result = isin + exch + level + noise
        assert (
            len(result) != chunk_size * 1024
        ), f"Chunk size missmatch {header_sz + noise_len} != {chunk_size * 1024}"
        return result

    def fill_binary_file(self, date: str, num_records: int, chunk_size: KByte):
        year, month, day = date.split("-")
        path = os.path.join(
            G_DATA_FOLDER, year, month, day, f"{self.instrument}@{self.exchange}.dat"
        )

        print(f"====Writing test data {self.instrument}@{self.exchange} ... ", end="")
        with open(path, "wb") as f:
            for _ in range(num_records):
                f.write(self.__produce_binary_chunk(chunk_size))
        print("OK")


def generate_dates(
    begin: datetime, end: datetime, chance_of_missing: float = 0.5
) -> list[str]:
    dropout_rate = int(chance_of_missing * 10)

    current = begin
    results: list[str] = []
    while current <= end:
        adate = f"{current.year}-{current.month}-{current.day}"
        current += timedelta(days=1)
        if rnd.randint(0, 10) < dropout_rate:
            continue
        results.append(adate)

    return results


G_SEED = 42069

if __name__ == "__main__":
    print("  Generating test data\n" f"==Fixed RND seed: {G_SEED}")
    rnd.seed(G_SEED)  # NOTE(iy): for reproducable noise

    payloads = (
        Payload("BTCETH", "Binance.spot", [0, 1, 2, 3]),
        Payload("BTCETH", "Okex.spot", [1, 2]),
        Payload("ETH_USDT", "Kucoin.spot", [0, 1, 2, 3, 4]),
        Payload("BTCETH_PERP", "Binance.fut", [0, 1, 2, 3]),
    )

    print("==Generating dates")
    dates = generate_dates(datetime(2023, 12, 25), datetime(2024, 1, 10))

    for date in dates:
        Manifest(date, payloads).create()

    print("Done!")
