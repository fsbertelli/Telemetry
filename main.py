import streamlit as st
import asyncio
import aiohttp
from time import sleep


async def get_robot_data(robot_id):
  url = f'http://espia:strongpiopio042@52.161.96.125:3001/robot.log?{robot_id}'
  async with aiohttp.ClientSession() as session:
    for retry in range(3):  # Retry up to 3 times
      try:
        async with session.get(url) as response:
          if response.status == 200:
            data = await response.text()
            parts = data.split(',')
            if len(parts) >= 33:
              rtk_status = int(parts[1])
              latitude = float(parts[2])
              longitude = float(parts[3])
              battery = round(float(parts[12]), 1)
              stop_button = int(parts[14])
              left_motor_alarm = int(parts[22])
              right_motor_alarm = int(parts[23])
              last_update = int(parts[32])
              return {
                  "robot_id": robot_id,
                  "rtk_status": rtk_status,
                  "latitude": latitude,
                  "longitude": longitude,
                  "battery": battery,
                  "stop_button": stop_button,
                  "left_motor_alarm": left_motor_alarm,
                  "right_motor_alarm": right_motor_alarm,
                  "status": last_update
              }
      except aiohttp.client_exceptions.ClientOSError as e:
        print(f"Error connecting to the server (Retry {retry + 1}/3): {e}")
        await asyncio.sleep(1)  # Add a small delay before retrying

  print(f"Failed to fetch data for robot {robot_id} after 3 retries.")
  return None


async def fetch_robot_data():
  robot_data = []
  robots = [
      1010, 1014, 1016, 1017, 1023, 1024, 1025, 1026, 1028, 1031, 1033, 1041,
      1042, 1043, 1044, 1046, 1047, 1049, 1050, 1051, 1055, 1060, 1061, 1062,
      1068, 1069, 1070, 1071, 1097, 1098, 1099
  ]

  async with aiohttp.ClientSession() as session:
    tasks = [get_robot_data(robot_id) for robot_id in robots]
    results = await asyncio.gather(*tasks)

    for data in results:
      if data is not None:
        robot_data.append(data)

  return robot_data


def main():
  st.set_page_config(page_title="Solix Telemetry",
                     page_icon="🤖",
                     layout="wide",
                     initial_sidebar_state="auto",
                     menu_items={'About': "felipe.bertelli@solinftec.com"})
  st.title(' 🤖 Solix Telemetry 📊')

  # Use st.empty() to dynamically update content
  robot_data_container = st.empty()

  while True:
    robot_data = asyncio.run(fetch_robot_data())

    # Create a table with the retrieved data
    table_data = {
        "Robot ID": [int(data["robot_id"]) for data in robot_data],
        "RTK Status": [data["rtk_status"] for data in robot_data],
        "Position":
        [f"{data['latitude']}, {data['longitude']}" for data in robot_data],
        "Battery": [round(data["battery"], 2) for data in robot_data],
        "Stop Button": [data["stop_button"] for data in robot_data],
        "Left Motor Alarm": [data["left_motor_alarm"] for data in robot_data],
        "Right Motor Alarm":
        [data["right_motor_alarm"] for data in robot_data],
        "Last Update": [data["status"] for data in robot_data]
    }

    robot_data_container.dataframe(table_data,
                                   hide_index=True,
                                   use_container_width=True,
                                   height=1000)

    for data in robot_data:
      if data["rtk_status"] != 44:
        st.toast(f'Robot {data["robot_id"]} RTK issues', icon='📡')
        asyncio.sleep(1)
      elif data["status"] != 0:
        st.toast(f'Robot {data["robot_id"]} connection issues', icon='🛜')
        asyncio.sleep(1.15)
      elif data["left_motor_alarm"] == 1 or data["right_motor_alarm"] == 1:
        st.toast(f'Robot {data["robot_id"]} motor alarm', icon='🛞')
        asyncio.sleep(1.20)
      elif data["stop_button"] != 0:
        st.toast(f'Robot {data["robot_id"]} stop button pressed', icon='🚨')
        asyncio.sleep(1.25)
      elif data["battery"] < 48.0:
        st.toast(f'Robot {data["robot_id"]} LOW BATTERY', icon='🪫')
        asyncio.sleep(1.30)
      #else:
      #   robot_data_container.table(table_data)
      #  st.balloons()

    # Update the content inside the container with the table

    # Add a delay to control the update frequency


if __name__ == '__main__':
  main()
