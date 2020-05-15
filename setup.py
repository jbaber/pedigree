from setuptools import setup, find_packages

with open('README.md') as f:
  long_description = "".join([line for line in f])

if __name__ == "__main__":
    setup(
        name='pedigree',
        description='Store family trees in plain text and visualize them in your browser',
        license='GPL',
        url='https://github.com/jbaber/pedigree',
        author='John Baber-Lucero',
        author_email="python@frundle.com",
        long_description=long_description,
        packages=find_packages(where="src"),
        entry_points = {
          'console_scripts': ['pedigree=pedigree.main:main'],
        },
        package_dir={"": "src"},
        zip_safe=False,
        install_requires=["docopt", "hashids", "networkx", "toml",],
        include_package_data=True,
        data_files=[('examples', ['examples/example.toml'])],
        version="1.0.0",
    )
