import openeo

# This will be required to import onnxruntime in the UDF.
dependencies_url = "https://artifactory.vgt.vito.be:443/auxdata-public/openeo/onnx_dependencies_1.16.3.zip"
# You can upload your own model and paste the url here.
model_url = "https://artifactory.vgt.vito.be:443/auxdata-public/openeo/test_onnx_model.zip"

spatial_extent = {"west": 8.908, "south": 53.791, "east": 8.96, "north": 54.016}
temporal_extent = ["2022-10-01", "2022-12-01"]

connection = openeo.connect("openeo.dataspace.copernicus.eu").authenticate_oidc()

s2_cube = connection.load_collection(
    "SENTINEL2_L2A",
    temporal_extent=temporal_extent,
    spatial_extent=spatial_extent,
    bands=["B04"],
    max_cloud_cover=20,
)

# We do not need a time dimesion for the UDF, so we remove it.
s2_cube_timeless = s2_cube.min_time()

udf = openeo.UDF.from_file("onnx_udf.py")
s2_cube = s2_cube.apply_neighborhood(
    udf,
    size=[{"dimension": "x", "value": 256, "unit": "px"}, {"dimension": "y", "value": 256, "unit": "px"}],
    overlap=[{"dimension": "x", "value": 64, "unit": "px"}, {"dimension": "y", "value": 64, "unit": "px"}],
)

# We pass the model and dependencies as zip files to the UDF through the job options.
# The zip files provided in this list will be extracted in the UDF environment in a folder indicated by the name after the # symbol.
job_options = {
    "udf-dependency-archives": [
        f"{dependencies_url}#onnx_deps",
        f"{model_url}#onnx_models",
    ],
}
s2_cube.execute_batch("output.nc", job_options=job_options)
