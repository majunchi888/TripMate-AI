import asyncio

from mcp_client import aviation_mcp_call


async def test_future_flights():

    date = "2026-08-22"

    print("=" * 60)
    print("测试 future_flights_arrival_departure_schedule")
    print("=" * 60)

    # ============================================================
    # 北京首都机场 PEK：未来出发航班
    # ============================================================

    print("\n>>> PEK departure")

    try:
        result = await aviation_mcp_call(
            "future_flights_arrival_departure_schedule",
            {
                "airport_iata_code": "PEK",
                "schedule_type": "departure",
                "date": date,
                "number_of_flights": 5
            }
        )

        print("【PEK 原始返回】")
        print(result)

    except Exception as e:
        print(
            f"PEK 调用失败: "
            f"{type(e).__name__}: {e}"
        )

    print("-" * 60)

    # ============================================================
    # 东京成田机场 NRT：未来到达航班
    # ============================================================

    print("\n>>> NRT arrival")

    try:
        result = await aviation_mcp_call(
            "future_flights_arrival_departure_schedule",
            {
                "airport_iata_code": "NRT",
                "schedule_type": "arrival",
                "date": date,
                "number_of_flights": 5
            }
        )

        print("【NRT 原始返回】")
        print(result)

    except Exception as e:
        print(
            f"NRT 调用失败: "
            f"{type(e).__name__}: {e}"
        )

    print("=" * 60)
    print("测试结束")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_future_flights())