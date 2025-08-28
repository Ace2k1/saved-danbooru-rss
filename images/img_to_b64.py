import base64
import os
def image_to_base64(image_path, output_txt):
    # Open image in binary mode
    with open(image_path, "rb") as image_file:
        # Encode to base64
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")

    # Save to text file
    with open(output_txt, "w") as text_file:
        text_file.write(encoded_string)

    print(f"Base64 string saved to {output_txt}")


# Example usage
if __name__ == "__main__":
    path = 'images'
    # Output files
    image_path = os.path.join(path, 'ouji_misao.png')
    output_txt = os.path.join(path, 'output.txt')
    # image_path = "ouji_misao.png"   # change to your image
    # output_txt = "output.txt"    # change to your desired text file name
    image_to_base64(image_path, output_txt)
