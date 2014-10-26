guard 'shell' do
  watch(%r{(.*)\.rst}) do |m|
    system("sphinx-build -b html -d build/doctrees source build/html")
  end
end

guard 'livereload' do
  watch(%r{(.*)\.rst})
end
