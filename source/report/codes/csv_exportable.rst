.. code-block:: ruby

  # app/models/concerns/csv_exportable.rb
  require 'csv'

  module CsvExportable
    extend ActiveSupport::Concern

    module ClassMethods
      def to_csv(header: column_names, columns: column_names, row_sep: "\r\n", encoding: Encoding::CP932)
        records = CSV.generate(row_sep: row_sep) do |csv|
          csv << header
          all.each { |record| csv << record.attributes.values_at(*columns) }
        end
        records.encode(encoding, invalid: :replace, undef: :replace)
      end
    end
  end


